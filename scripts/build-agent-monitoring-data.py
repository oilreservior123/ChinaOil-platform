#!/usr/bin/env python3
"""Rebuild browser monitoring datasets from downloaded genuine public datasets.

Usage: PYTHONPATH=/path/to/pyarrow python scripts/build-agent-monitoring-data.py
       [--source-root /path/to/reservoir_datasets]
No dates, labels, missing sensor values, or spatial coordinates are synthesized.
"""
import argparse
import configparser
import json
import math
import shutil
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / 'dist/agent/data'


def save(name, rows):
    target = OUT / name
    target.write_text(json.dumps(rows, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n')
    print(f'{name}: {len(rows)} rows; {target.stat().st_size:,} bytes')


def number(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def sensor_summary(frame, candidates, divisor):
    """First sensor with finite measurements; zeros are real data, never missing."""
    for column in candidates:
        if column not in frame:
            continue
        values = pd.to_numeric(frame[column], errors='coerce').to_numpy(dtype=float)
        values = values[np.isfinite(values)] / divisor
        if values.size:
            return column, int(values.size), [float(values.mean()), float(values.std(ddof=0)), float(values[-1] - values[0])]
    return None, 0, [None, None, None]


def build_threew(source):
    root = source / '02_3W_real/dataset'
    config = configparser.ConfigParser()
    config.read(root / 'dataset.ini')
    labels = {int(config[section]['LABEL']): config[section]['DESCRIPTION'] for section in config.sections() if 'LABEL' in config[section]}
    pressure = ['P-PDG', 'P-TPT', 'PT-P', 'P-MON-CKP', 'P-JUS-CKP']
    temperature = ['T-TPT', 'T-PDG', 'T-MON-CKP', 'T-JUS-CKP']
    rows = []
    for path in sorted(root.glob('[0-9]/WELL-*.parquet')):
        frame = pd.read_parquet(path)
        # Prefer the observed stable event; decode documented transient offset
        # only when no stable event exists. Never turn a transient event into normal.
        classes = pd.to_numeric(frame['class'], errors='coerce')
        stable = classes[classes.isin(labels)].astype(int)
        class_values = sorted(int(value) for value in classes.dropna().unique())
        event_code = int(path.parent.name)
        label_basis = 'stable_class'
        if event_code not in set(stable):
            offset = int(config['EVENTS']['TRANSIENT_OFFSET'])
            transient = [value - offset for value in class_values if value - offset in labels and value >= offset]
            if event_code in transient:
                label_basis = 'transient_class_offset'
            else:
                nonnormal = stable[stable != 0]
                event_code = int((nonnormal if len(nonnormal) else stable).mode().iloc[0]) if len(stable) else None
                label_basis = 'stable_class_mode' if event_code is not None else 'missing_class'
        ps, pn, p = sensor_summary(frame, pressure, 1e6)
        ts, tn, t = sensor_summary(frame, temperature, 1)
        missing = [key for key, value in zip(['p_mean','p_std','p_delta','t_mean','t_std','t_delta'], p + t) if value is None]
        rows.append({'well_id': path.stem.split('_')[0], 'event_id': path.name,
                     'source_filename': path.relative_to(root).as_posix(), 'sample_count': len(frame),
                     'event_code': event_code, 'event_label': labels.get(event_code),
                     'label': None if event_code is None else int(event_code != 0),
                     'p_mean': p[0], 'p_std': p[1], 't_mean': t[0], 't_std': t[1],
                     'p_delta': p[2], 't_delta': t[2], 'pressure_sensor': ps, 'temperature_sensor': ts,
                     'pressure_sample_count': pn, 'temperature_sample_count': tn,
                     'missing_features': missing, 'summary_complete': not missing,
                     'training_eligible': not missing and event_code is not None,
                     'pressure_unit': 'MPa', 'temperature_unit': '°C',
                     'stable_class_count': len(stable), 'source_event_code': int(path.parent.name),
                     'class_values': class_values, 'label_basis': label_basis,
                     'transient_only': label_basis == 'transient_class_offset'})
    assert len(rows) == 1119, len(rows)
    save('threew-events.json', rows)
    return rows


def build_esp(source):
    frame = pd.read_csv(source / '05_ESPset/features.csv', sep=';')
    keys = {'median(8,13)': 'f_low', 'rms(98,102)': 'f_rms', 'median(98,102)': 'f_near', 'peak1x': 'f_1x', 'peak2x': 'f_2x', 'a': 'f_a', 'b': 'f_b'}
    rows = []
    for r in frame.to_dict('records'):
        rows.append({'well_id': f"ESP-{int(r['esp_id'])}", 'sample_id': int(r['id']),
                     'esp_id': int(r['esp_id']), 'fault': r['label'],
                     **{target: number(r[original]) for original, target in keys.items()}})
    assert len(rows) == 6032
    save('esp-features.json', rows)
    return rows


def build_dst(source):
    root = source / '04_DST/extracted'
    rows = []
    files = sorted(root.rglob('DST_Data*.csv'))
    for path in files:
        for index, r in enumerate(pd.read_csv(path).to_dict('records')):
            phase = None if pd.isna(r['Period']) else str(r['Period'])
            pressure = number(r['Pressure (psi)'])
            rows.append({'well_id': path.parent.name,
                         'test_id': f'{path.parent.name}:{path.stem}:{phase or ""}',
                         'source_filename': path.relative_to(root).as_posix(),
                         'test_phase': phase, 'sample_id': f'{path.parent.name}:{path.stem}:{index + 1}',
                         'log_horner': number(r['Log time']),
                         'pressure': None if pressure is None else pressure * 0.006894757,
                         'time_min': number(r['Time (min)'])})
    save('dst.json', rows)
    return rows, len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=REPO.parent / 'reservoir_datasets')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    downloads = OUT / 'downloads'
    downloads.mkdir(exist_ok=True)
    threew = build_threew(args.source_root)
    esp = build_esp(args.source_root)
    dst, dst_files = build_dst(args.source_root)
    for original, name in [('01_Volve/Volve_production_data.xlsx', 'Volve_production_data.xlsx'), ('04_DST/Sweetwater_DST_V2_original.zip', 'Sweetwater_DST_V2_original.zip'), ('05_ESPset/features.csv', 'ESPset_features.csv')]:
        shutil.copyfile(args.source_root / original, downloads / name)
    volve = json.loads((OUT / 'volve.json').read_text())
    catalog = [
        {'id':'volve','title':'Volve 真实生产日报','description':'Equinor Volve 逐井生产日报；无现场确诊故障标签。注水量为全油田每日合计，不代表井对分配。','available':True,'path':'./data/volve.json','count':len(volve),'unit_notes':'产油/水/液 m³/d；气量 Sm³/d；压力 MPa；含水率 %。','source_url':'https://www.equinor.com/energy/volve-data-sharing','download_url':'./data/downloads/Volve_production_data.xlsx','models':['rules','arps','crm','tcn','stgnn','gdn','diagnosis','pinn'],'limitations':'diagnosis 缺少确诊 root_cause；PINN 缺少真实空间 x 与归一化 t；须上传补齐，不能直接训练这两个模型。','raw_download_url':'https://www.equinor.com/energy/volve-data-sharing'},
        {'id':'threew','title':'3W 真实井事件摘要','description':'全部 1119 个 WELL 实测文件各形成一个事件摘要；不含模拟/手绘文件，也不是完整原始时序。保留真实井号、事件文件名和观测标签。','available':True,'path':'./data/threew-events.json','count':len(threew),'unit_notes':'p_mean/p_std/p_delta MPa；t_mean/t_std/t_delta °C；std 为总体标准差；delta 为末个减首个有限测量。','source_url':'https://github.com/petrobras/3W','download_url':'./data/threew-events.json','raw_download_url':'https://github.com/petrobras/3W/tree/8aaa303f9b9d6ced690d136218d141624b10558d/dataset','models':['event3w'],'limitations':'缺测摘要为 null 并标记；优先 P-PDG/T-TPT，缺测才用文档列明的实际传感器。事件级摘要仅支持事件分类，不能替代时序预测。'},
        {'id':'dst','title':'Sweetwater DST 真实压力恢复','description':f'{dst_files} 个 DST_Data 文件的原始压力恢复记录；排除 Overview 与 Analysis 汇总文件。','available':True,'path':'./data/dst.json','count':len(dst),'unit_notes':'pressure MPa（原 psi × 0.006894757）；time_min 分钟；log_horner 直接保留原 Log time，即 log10(H)。','source_url':'https://data.mendeley.com/datasets/px455bwjg2/2','download_url':'./data/downloads/Sweetwater_DST_V2_original.zip','raw_download_url':'https://data.mendeley.com/public-api/zip/px455bwjg2/download/2','models':['horner','pinn'],'limitations':'Horner 使用 log_horner；PINN 缺少实测空间坐标 x，且需用户明确归一化 t，当前内置数据不能直接训练 PINN。'},
        {'id':'esp','title':'ESPset 真实振动特征','description':'完整 6032 行原始特征；保留 ESP 编号、样本编号与原始故障标签；无虚构日期。','available':True,'path':'./data/esp-features.json','count':len(esp),'unit_notes':'保留源特征数值尺度；f_low=median(8,13), f_rms=rms(98,102), f_near=median(98,102), f_1x=peak1x, f_2x=peak2x, f_a=a, f_b=b；源 CSV 未逐列声明物理单位。','source_url':'https://data.mendeley.com/datasets/m268jsw339/3','download_url':'./data/downloads/ESPset_features.csv','raw_download_url':'https://data.mendeley.com/public-api/zip/m268jsw339/download/3','models':['esp']},
        {'id':'tracer','title':'Spraberry 示踪剂（待上传）','description':'来源网站安全验证阻断下载，未取得数据。仅提供用户上传入口，不生成或替代真实测量。','available':False,'path':None,'count':0,'unit_notes':'上传时指定真实浓度、时间与单位。','source_url':'https://oaktrust.library.tamu.edu/items/3eb9a1e3-2dba-486c-9c04-d25a2e95d270/full','download_url':None,'raw_download_url':'https://oaktrust.library.tamu.edu/items/3eb9a1e3-2dba-486c-9c04-d25a2e95d270/full','models':['tracer']}
    ]
    save('catalog.json', catalog)
    print('3W event counts:', dict(Counter(r['event_code'] for r in threew)))
    print('3W missing summaries:', sum(not r['summary_complete'] for r in threew))
    print('3W pressure sensors:', dict(Counter(r['pressure_sensor'] for r in threew)))
    print('3W temperature sensors:', dict(Counter(r['temperature_sensor'] for r in threew)))
    print('ESP faults:', dict(Counter(r['fault'] for r in esp)))
    print('DST wells/tests:', len({r['well_id'] for r in dst}), len({r['test_id'] for r in dst}))
    print('DST missing:', {k:sum(r[k] is None for r in dst) for k in ['time_min','log_horner','pressure']})


if __name__ == '__main__':
    main()
