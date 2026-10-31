import{esc}from'./ui.mjs';
const code='https://github.com/oilreservior123/ChinaOil-platform/blob/main/';
const M=(name,kind,equations,symbols,layers,note,source)=>({name,kind,equations,symbols,layers,note,source});
export const MODEL_THEORY={
 isolation_forest:M('Isolation Forest · 孤立森林','异常检测',[
 ['异常度', 's(x,n) = 2<sup>−E[h(x)] / c(n)</sup>'],['路径归一化','c(n) = 2H<sub>n−1</sub> − 2(n−1)/n'],['平台判定','a(x) = s(x,n) + offset；异常 ⇔ a(x) ≥ θ']],
 'x：测井特征向量；h：孤立树路径长度；E：森林平均；n：每树抽样数；H：调和数，代码采用对数近似；offset：已训练森林偏移；θ：验证集选择或既定阈值。分数为无量纲。',
 [['GR / RHOB / DTC'],['训练集缺失中位数与稳健标准化'],['随机孤立树森林','专业物理规则'],['路径平均评分 / 规则复核'],['异常候选与质量标识']],
 '异常分数不同于异常概率；人工尖峰评价不能代替现场专家异常金标准。', 'backend/classical_models.py'),
 grin:M('GRIN · 图循环插补网络精简复现','缺失重建',[
 ['图消息','n<sub>t</sub> = A h<sub>t−1</sub>；g<sub>t</sub> = A x̃<sub>t</sub>'],['循环编码','h<sub>t</sub> = GRU(tanh(W[x̃<sub>t</sub>,m<sub>t</sub>,g<sub>t</sub>,n<sub>t</sub>] + b), h<sub>t−1</sub>)'],['双向融合','x̂<sub>t</sub> = (x̂<sub>t</sub><sup>→</sup> + x̂<sub>t</sub><sup>←</sup>)/2'],['遮蔽训练','L = Σ<sub>t,i,c</sub> H<sub>tic</sub>(x̂<sub>tic</sub> − x<sub>tic</sub>)² / ΣH；x<sub>out</sub> = m⊙x + (1−m)⊙x̂']],
 'A：仅由训练期统计生成的行归一化井网络邻接；m：可见观测掩码；H：人工遮蔽的已知真值位置；x̃：缺失位置的循环填充值；⊙：逐元素乘法。损失在训练期标准化空间计算。',
 [['多井时间序列 + 观测掩码'],['训练期邻接与标准化'],['正向图消息 GRU','反向图消息 GRU'],['双向输出平均'],['保留已知值 / 缺失值重建'],['物理越界与长缺口复核']],
 '共享参数双向图消息 GRU（隐藏维度16），属于精简结构复现；天然缺失无真值，不据此报告插补准确率。','backend/deep_models.py'),
 uie:M('UIE 式统一知识抽取精简结构','跨度抽取',[
 ['提示条件编码','H = Transformer(Embed([提示；正文]) + Position)'],['起止位置','p<sub>s</sub> = softmax(W<sub>s</sub>H+b<sub>s</sub>)；p<sub>e</sub> = softmax(W<sub>e</sub>H+b<sub>e</sub>)'],['训练目标','L = −log p<sub>s</sub>(s*) − log p<sub>e</sub>(e*)'],['本体复核','输出 = Span(ŝ,ê)；检查 类型 ∈ 本体、正文起止有效、证据可定位']],
 'H：字符级上下文表征；s*、e*：人工或模板标注的起止位置；p：正文位置上的概率；独立服务内部end为包含位置，接口end采用不包含右端点的字符索引。',
 [['抽取提示 + 中文正文'],['字符嵌入与位置编码'],['提示条件 Transformer'],['起点分类头','终点分类头'],['正文跨度解码'],['本体类型复核与来源追溯']],
 '这是本项目的提示条件跨度模型，不是官方UIE预训练模型。新训练服务为1层32维4头；历史基准为另一精简配置，不混用。','backend/deep_models.py'),
 rotate:M('RotatE · 复数空间关系旋转','关系预测',[
 ['关系旋转','r = exp(iθ) = cosθ + i sinθ；h ⊙ r ≈ t'],['评分函数','f(h,r,t) = γ − Σ<sub>k</sub> |h<sub>k</sub>r<sub>k</sub> − t<sub>k</sub>|'],['训练目标','L = −½[平均 log σ(f<sup>+</sup>) + 平均 log σ(−f<sup>−</sup>)]']],
 'h、t：头尾实体复数向量；r：模长为1的关系向量；θ：相位；γ：间隔常数；σ：逻辑函数；正负样本分数记为f⁺、f⁻。分数无量纲，并非连通概率。',
 [['井—层—井组三元组'],['实体复数嵌入 h,t','关系相位嵌入 θ'],['逐维旋转 h⊙r'],['复数残差模长求和'],['候选实体评分与排名']],
 '训练服务采用均匀负采样并忽略训练已知正例；历史实验的采样配置单独记录。验证选模只过滤训练与验证事实，测试不参与权重选择。','backend/deep_models.py'),
 anomaly_transformer:M('Anomaly Transformer · 关联差异异常检测','时序检测',[
 ['序列与先验关联','S = softmax(QKᵀ/√d<sub>h</sub>)；P<sub>ij</sub> ∝ exp[−(i−j)²/(2σ<sub>i</sub>²)]'],['关联差异','D<sub>i</sub> = 平均<sub>头</sub>[KL(S<sub>i</sub>∥P<sub>i</sub>) + KL(P<sub>i</sub>∥S<sub>i</sub>)]'],['异常分数','a<sub>i</sub> = T · softmax(−D)<sub>i</sub> · 平均<sub>特征</sub>(x̂<sub>i</sub>−x<sub>i</sub>)²'],['精简训练目标','L = L<sub>重建</sub> + 0.01D(stopgrad(S),P) − 0.01D(S,stopgrad(P))']],
 'Q、K：查询和键；dₕ：单头维度；P：逐行归一化的高斯位置先验；T：窗口长度；KL：相对熵；stopgrad：阻断该分支梯度。σ为窗口索引尺度，不是压力或时间的计量单位。',
 [['产油 / 产液 / 含水 / 压力 / 注水'],['训练统计填补与标准化'],['序列注意力关联 S','高斯位置先验 P'],['关联差异 + 重建头'],['重建误差与差异加权'],['验证阈值 / 异常时段']],
 '新服务为1层24维2头、按井日期排序的32点窗口；精简同一步梯度优化，不宣称等同官方训练。阈值仅用训练或验证数据。','backend/deep_models.py'),
 arps:M('Arps · 产量递减模型','机理基线',[
 ['双曲递减','q(t) = q<sub>i</sub> / (1 + bD<sub>i</sub>t)<sup>1/b</sup>'],['指数极限','b → 0：q(t) = q<sub>i</sub> exp(−D<sub>i</sub>t)'],['参数校准','训练：最小化残差；验证：选择 RMSE 最小的候选参数；测试：独立外推']],
 'q、qᵢ：产油率，标准立方米/日；Dᵢ：初始递减率，日⁻¹；t：累计天数；b：无量纲递减指数。浏览器采用产量残差网格拟合；训练服务对数产量残差拟合，再按验证产量RMSE选b。',
 [['单井稳定生产窗口'],['训练期 qi / Di / b 候选拟合'],['验证期误差选参'],['测试期与未来产量外推'],['偏离基线与适用性校验']],
 '生产制度与递减流动条件须经工程确认；停井、措施切换等时段不直接解释为自然递减。','backend/classical_models.py'),
 crm:M('CRM · 注采响应模型','动态响应',[
 ['一阶响应','τ du<sub>j</sub>/dt + u<sub>j</sub> = I<sub>j</sub>(t)'],['实际离散更新','u<sub>j,k</sub> = exp(−Δt/τ)u<sub>j,k−1</sub> + [1−exp(−Δt/τ)]I<sub>j,k</sub>'],['产液拟合','q̂<sub>L,k</sub> = c + Σ<sub>j</sub> f<sub>j</sub>u<sub>j,k</sub>；(f,c) ≥ 0']],
 'I：注水率；qL：产液率；u：滤波响应，均为同一口径标准立方米/日；τ、Δt：响应时间与真实日历间隔，单位日；f：无量纲响应权重；c：基线产液率。',
 [['按日期对齐的双注水信号'],['候选响应时间 τ'],['一阶状态滤波与日期传递'],['非负最小二乘 f / c'],['验证选 τ / 独立测试'],['产液响应与参数解释']],
 '本服务采用两注水信号、单产液响应的简化模型，不把响应拟合权重直接认定为现场水力连通。','backend/classical_models.py'),
 dfn:M('DFN · 应力方向加权裂缝几何','几何模型',[
 ['裂缝几何','L = √[(x₂−x₁)²+(y₂−y₁)²]；θ = atan2(y₂−y₁,x₂−x₁)'],['方向权重假设','w = ρ + (1−ρ)cos²(θ−θ<sub>σ</sub>)'],['等效开度','a<sub>eff</sub> = a₀ w；0 ≤ ρ ≤ 1']],
 'x、y、L：米；a₀、aₑff：毫米；θ：裂缝方向；θσ：输入应力方向，角度转换为弧度后计算；ρ：无量纲方向权重下限。本式是声明的演示假设。',
 [['公开裂缝端点几何'],['长度与方向统计'],['输入应力方向与权重下限'],['方向权重与等效开度'],['交点 / 网络连边'],['几何统计与候选方案展示']],
 '未求解完整地应力平衡或裂缝扩展方程，不能称为已校准的地质力学预测。DFN候选方案当前仅展示；EDFM使用固定公开基准耦合图，未由该方案实时重建。','backend/classical_models.py'),
 edfm:M('EDFM · 嵌入式裂缝油水两相渗流','数值模拟',[
 ['压力与界面通量','Σ<sub>j</sub> q<sub>ij</sub> = Q<sub>i</sub>；q<sub>ij</sub> = T<sub>ij</sub> λ<sub>t,ij</sub>(p<sub>i</sub>−p<sub>j</sub>)'],['相流动度与分流','λ<sub>t</sub> = k<sub>rw</sub>/μ<sub>w</sub> + k<sub>ro</sub>/μ<sub>o</sub>；f<sub>w</sub> = (k<sub>rw</sub>/μ<sub>w</sub>)/λ<sub>t</sub>'],['隐式水相守恒','PV<sub>i</sub>(S<sub>i</sub><sup>n+1</sup>−S<sub>i</sub><sup>n</sup>)/Δt + Σ<sub>出</sub> q f<sub>w,i</sub><sup>n+1</sup> − Σ<sub>入</sub>|q|f<sub>w,上游</sub><sup>n+1</sup> = Q<sub>w,i</sub>'],['Corey 型相渗假设','S<sub>e</sub> = clip[(S<sub>w</sub>−0.15)/0.70,0,1]；k<sub>rw</sub> = S<sub>e</sub>²；k<sub>ro</sub> = (1−S<sub>e</sub>)²']],
 'T：基质—基质、基质—裂缝、裂缝—裂缝连接的几何传导系数；p内部为帕，展示为兆帕；q、Q内部为立方米/秒，输出为立方米/日；PV为孔隙体积，立方米；S、kr、fw无量纲；μ为帕·秒；Δt内部为秒。',
 [['基质网格 + 显式裂缝自由度'],['组装三类连接与孔隙体积'],['压力系统 PCG 求解'],['界面通量与上游方向'],['保守隐式饱和度更新'],['下一时间步 / 产量与守恒评价']],
 '精简二维、不可压缩油水算例；相流动度用调和平均连接，孔隙与传导随开度缩放。未包含气相、重力、毛管压力或全耦合地质力学。','dist/physics-runtime.mjs'),
 entity_align:M('语义实体对齐 · 字典与字符基线','规范对齐',[
 ['名称规范化','N(s) = 字符归一化 / 空白与编码分隔处理'],['网页候选相似度','J(A,B) = |A∩B| / |A∪B|'],['服务别名匹配','score = 2M/(|a|+|b|)；score ≥ θ 才接受候选']],
 'A、B：规范名称的字符集合；服务中M为SequenceMatcher的匹配字符数；a、b为规范别名串；θ默认0.8。精确标准编码或已知别名匹配优先。分数无量纲。',
 [['井号 / 术语 / 别名'],['编码与名称规范化'],['精确编码 / 字典匹配'],['字符集合或序列相似度'],['标准实体候选与人工复核']],
 '网页采用字符Jaccard候选；独立训练服务采用别名字典与SequenceMatcher，两种实现明确区分，均不是神经语义嵌入模型。','backend/auxiliary_models.py'),
 lag:M('动态时滞 · 日历对齐 Pearson 关联','描述统计',[
 ['时滞相关','r(ℓ) = Σ(x<sub>t</sub>−x̄)(y<sub>t+ℓ</sub>−ȳ) / √[Σ(x<sub>t</sub>−x̄)² Σ(y<sub>t+ℓ</sub>−ȳ)²]'],['候选时滞','ℓ* = argmax<sub>ℓ</sub> |r(ℓ)|']],
 'x：注水序列；y：生产序列，单位按输入口径统一；ℓ为日历时滞，单位日；r无量纲。只统计日期可对齐且非缺失的配对，常数序列不计算相关系数。',
 [['注水 / 生产日序列'],['真实日历日期对齐'],['逐候选时滞配对'],['Pearson 相关与样本量'],['最大绝对相关时滞候选']],
 '相关不等于因果，也不能代替注采连通性的机理或示踪试验确认。网页历史分析使用冻结训练期窗口。','dist/algorithms.mjs'),
 hierarchy:M('单井主数据与井—层—井组—区块图','数据关联',[
 ['唯一主键','井对象主键 K = 标准井唯一编码'],['有效时间约束','有效关系 ⇔ valid_from ≤ 查询日期 ≤ valid_to'],['层级汇聚','Q<sub>对象</sub> = Σ<sub>去重井号</sub> Q<sub>井</sub>；f<sub>w</sub> = ΣV<sub>w</sub> / (ΣV<sub>o</sub> + ΣV<sub>w</sub>)']],
 'K：井唯一编码，无量纲标识；Vo、Vw：同一统计时段的标准立方米累计体积；fw为含水比例，无量纲。井组综合含水以体积加权，不平均各井百分比。',
 [['标准井唯一编码'],['单井专业记录与日期对齐'],['井—层有效关系','井组—区块有效关系'],['冲突 / 重叠区间检查'],['去重汇聚与多级关联图']],
 '目前展示的井组、小层和区块归属含明确生成映射，不代表已验证的真实地质或水力边界。','backend/auxiliary_models.py'),
 rules:M('油藏专业规则 · 联合质量控制','确定性规则',[
 ['物理与比例约束','q<sub>o</sub>, q<sub>L</sub>, p, I ≥ 0；0 ≤ f<sub>w</sub> ≤ 1；q<sub>o</sub> ≤ q<sub>L</sub>'],['油液含水一致性','|f<sub>w</sub> − (1−q<sub>o</sub>/q<sub>L</sub>)| ≤ ε；q<sub>L</sub> > 0'],['跨专业一致性','|z<sub>测井</sub>−z<sub>岩心</sub>| ≤ 2 米；|φ<sub>测井</sub>−φ<sub>岩心</sub>| ≤ 0.04']],
 'qo、qL、I：同口径体积率；p：确认口径的压力；fw、φ：无量纲比例；z：米；ε为配置的容差，独立服务默认0.05，网页规则按数据口径采用自己的容差。',
 [['多源记录 / 单位与主键'],['完整性 / 重复 / 时间对齐'],['物理取值规则','跨专业一致性规则'],['L0 阻断 / L1 提醒'],['质量标识与人工处置']],
 '规则是可检查的业务约束，不需要神经网络训练；异常标签仅作候选筛查。','backend/auxiliary_models.py'),
 ontology:M('领域本体 · 类型与关系约束','知识规范',[
 ['知识事实','G = (V,E)；事实 = (头实体, 关系, 尾实体, 来源)'],['类型有效性','有效(e) ⇔ type(head) ∈ domain(r) 且 type(tail) ∈ range(r)'],['证据追溯','抽取属性必须具有 标准实体编码 + 来源文档 / 字段 + 有效时间']],
 'V、E：实体与关系集合；domain、range：关系两端允许的本体类型；本体约束为知识治理原则，不是学习型评分。井位、层系、措施等术语依字典规范。',
 [['井 / 层位 / 措施术语字典'],['实体类型与属性规范'],['关系类型 / 头尾类型约束'],['抽取结果与实体对齐'],['证据与来源记录'],['结构化知识关联图']],
 '平台提供词典规范、类型及证据复核；没有实现通用OWL逻辑推理器或全量SHACL校验引擎，不宣称具备这些能力。','dist/algorithms.mjs'),
 retrieval:M('业务语义检索 · 同义词与字符排序','检索基线',[
 ['同义词与分词','Q = tokens(同义词归一化(查询))'],['网页实际排序','score(d,Q) = Σ<sub>u∈Q∩tokens(d)</sub> w(u) / √|tokens(d)|'],['当前词权重','w(u) = 4（含数字）；2（多字符）；1（单字符）']],
 'tokens包含英文/数字词、中文字符及相邻二元组；同义词映射覆盖产油、产水等业务表达；d为证据文本。分数只用于候选排序，无量纲。',
 [['业务问题 / 井号 / 时间'],['本体同义词归一化'],['字符与相邻二元组分词'],['匹配词加权 / 长度归一化'],['证据排序与来源查询']],
 '这是当前代码的可追溯检索基线，不是BGE向量检索，也不是生成式问答模型。','dist/algorithms.mjs'),
 historical:M('历史异常模式匹配','案例关联',[
 ['模式相似度','J(P<sub>q</sub>,P<sub>h</sub>) = |P<sub>q</sub>∩P<sub>h</sub>| / |P<sub>q</sub>∪P<sub>h</sub>|'],['动态差异','d = Σ<sub>可比指标</sub>|Δ<sub>当前</sub>−Δ<sub>历史</sub>|'],['时间过滤','同井历史日期 < 当前日期 − 30 日；排除测试事件']],
 'P：异常模式标签集合；Δ：相对产油变化、含水比例差和相对压力变化，均无量纲。先按J降序，再按d升序排序，并去除近邻重复时段。',
 [['当前井 / 异常日期与模式'],['同井历史与时间隔离'],['模式集合 Jaccard'],['可比指标差异排序'],['历史候选事件与依据链']],
 '匹配到相似历史模式不等于确认根因，不输出未经验证的因果诊断。','dist/algorithms.mjs'),
 dag:M('DAG · 协同分析工作流','依赖编排',[
 ['拓扑依赖','G = (N,E) 为有向无环图；u→v ⇒ order(u) < order(v)'],['节点就绪','ready(v) = ∧<sub>u∈pred(v)</sub>[status(u) = completed]'],['质量门禁','存在 L0 阻断 ⇒ 下游不执行；新运行清除旧成功结果']],
 'N：分析节点；E：依赖关系；pred(v)：直接前驱；order：拓扑次序。编排器无需训练；界面记录每节点实际执行状态。',
 [['数据质控'],['知识证据关联','生产动态诊断'],['Arps 机理校验'],['裂缝装配 → EDFM 求解'],['产能评价 → 依据链导出']],
 '当前8节点按依赖顺序执行；两条分支共享质控依赖，但实现没有宣称并行计算或自动专家决策。','dist/app.js')
};
export function modelIdsForView(s){switch(s.route){case'quality':return s.qualityTab==='impute'?['grin','rules']:s.qualityTab==='rules'?['rules']:['isolation_forest','rules'];case'knowledge':return({graph:['ontology','hierarchy'],extract:['uie','ontology'],predict:['rotate'],temporal:['lag'],search:['entity_align','retrieval']})[s.graphTab]??['ontology'];case'well':return s.wellTab==='crm'?['crm']:s.wellTab==='temporal'?['lag']:['hierarchy'];case'diagnosis':return s.diagnosisTab==='decline'?['arps']:['anomaly_transformer','rules','historical'];case'simulation':return s.simTab==='dfn'?['dfn']:s.simTab==='validation'?['dfn','edfm']:['edfm'];case'workflow':return['dag','rules','hierarchy','anomaly_transformer','arps','dfn','edfm'];case'models':return s.modelId==='edfm'?['dfn','edfm']:[s.modelId??'isolation_forest'];default:return[]}}
function arch(layers,id,name){const w=600,step=71,height=layers.length*step+8;let centers=[];const nodes=layers.map((layer,k)=>layer.map((label,j)=>{const width=layer.length===1?464:264,x=layer.length===1?68:22+j*292,y=8+k*step;centers.push({layer:k,x:x+width/2,y});const chars=Array.from(label),parts=chars.length>19?[chars.slice(0,19).join(''),chars.slice(19).join('')]:[label];return`<g><rect x="${x}" y="${y}" width="${width}" height="48" rx="9"/><text x="${x+width/2}" y="${y+(parts.length>1?19:29)}" text-anchor="middle">${parts.map((t,i)=>`<tspan x="${x+width/2}" dy="${i?16:0}">${esc(t)}</tspan>`).join('')}</text></g>`}).join('')).join('');const edges=[];for(let k=0;k<layers.length-1;k++)for(const a of centers.filter(x=>x.layer===k))for(const b of centers.filter(x=>x.layer===k+1))edges.push(`<path d="M ${a.x} ${a.y+48} C ${a.x} ${a.y+62}, ${b.x} ${b.y-10}, ${b.x} ${b.y-3}" marker-end="url(#${id})"/>`);return`<svg class="theory-architecture" viewBox="0 0 ${w} ${height}" role="img" aria-label="${esc(name)}实现架构图"><title>${esc(name)}：${esc(layers.map(x=>x.join(' / ')).join(' → '))}</title><defs><marker id="${id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" class="arrow-head"/></marker></defs>${edges.join('')}${nodes}</svg>`}
export function renderModelTheory(ids,{scope='business'}={}){ids=[...new Set(ids)].filter(id=>MODEL_THEORY[id]);if(!ids.length)return'';return`<section class="model-theory-zone" aria-label="本区域模型公式与架构"><div class="theory-zone-title"><div><span class="eyebrow">MODEL PRINCIPLES / IMPLEMENTATION</span><h2>本区域模型 · 数学公式与实现架构</h2></div><span class="chip amber">${ids.length}项方法 · 对应当前功能</span></div>${ids.map(id=>{const m=MODEL_THEORY[id];return`<article class="theory-card" data-theory-model="${id}"><div class="theory-card-head"><h3>${esc(m.name)}</h3><span class="chip">${esc(m.kind)}</span></div><div class="theory-content"><div class="theory-mathematics">${m.equations.map(([label,formula])=>`<div class="equation-row"><span>${esc(label)}</span><div class="math-equation" role="math" aria-label="${esc(formula.replace(/<[^>]*>/g,''))}">${formula}</div></div>`).join('')}<p class="theory-symbols"><b>符号与单位：</b>${esc(m.symbols)}</p></div><div class="theory-diagram"><b>本项目实现结构</b>${arch(m.layers,`${scope}-${id}-arrow`,m.name)}</div></div><div class="theory-boundary"><b>实现边界：</b>${esc(m.note)}<a href="${code+m.source}" target="_blank" rel="noopener noreferrer">查看对应实现 ↗</a></div></article>`}).join('')}</section>`}
