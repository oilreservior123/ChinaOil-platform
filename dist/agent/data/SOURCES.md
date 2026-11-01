# Volve production browser data
Origin: Equinor Volve open dataset, https://www.equinor.com/energy/volve-data-sharing
Actual workbook mirror: https://github.com/Yuv7145/oil-well-production-analytics/blob/main/data/Volve%20production%20data.xlsx
Converted Daily Production Data production records; missing values retained as empty strings; pressure bar converted to MPa by multiplying 0.1.
water_cut is derived from oil and water volumes. injection is field-total daily injection summed from original injection rows, not a measured well-pair injection or allocation.
No confirmed fault, intervention, or commissioning labels have been invented. Source operation hours retained. Zeros preserved, require domain QC.
Use subject to Equinor Open Data Licence.
