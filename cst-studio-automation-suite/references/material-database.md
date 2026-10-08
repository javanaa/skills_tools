# 材料数据库使用说明

> 从 cst-studio-mcp (ismailakdag) 提取的材料数据库，含基板、金属、介质。

## 一、数据库文件

```
data/
├── substrates.json          # 常用 PCB/微波基板
├── common_metals.json       # 常用金属
└── common_dielectrics.json  # 常用介质材料
```

## 二、基板材料 (substrates.json)

### 高频微波基板
| 材料 | εr | tanδ | 厚度选项 | 用途 |
|------|-----|------|----------|------|
| RO4003C | 3.55 | 0.0027 | 8/20/32/60mil | 吸波超材料常用基准 |
| RO4350B | 3.48 | 0.0037 | 8/20/32/60mil | 高频 |
| RO5880 | 2.20 | 0.0009 | 5/10/20/31mil | 极低损耗 |
| RO3003 | 3.00 | 0.0013 | 7/10/20/30mil | 毫米波 |
| RT/duroid 6002 | 2.94 | 0.0012 | — | 高稳定 |
| RT/duroid 6006 | 6.15 | 0.0019 | — | 高介电 |
| RT/duroid 6010 | 10.20 | 0.0023 | — | 极高介电 |

### 普通 PCB
| 材料 | εr | tanδ | 用途 |
|------|-----|------|------|
| FR4 | 4.40 | 0.020 | 普通 PCB（损耗大） |
| FR4 High Tg | 4.30 | 0.015 | 耐高温 |
| CEM-1 | 4.20 | 0.025 | 单面 PCB |

## 三、金属材料 (common_metals.json)

| 材料 | 电导率 (S/m) | 用途 |
|------|-------------|------|
| Copper (annealed) | 5.8e7 | 铜层/背板 |
| Copper (pure) | 5.96e7 | 纯铜 |
| Gold | 4.1e7 | 镀金 |
| Silver | 6.3e7 | 镀银 |
| Aluminum | 3.77e7 | 铝 |
| Platinum | 9.4e6 | 铂 |
| Nickel | 1.45e7 | 镍 |
| Tin | 9.1e6 | 锡 |
| Lead | 4.8e6 | 铅 |

> CST 中金属层通常用 `Copper (annealed)` 或 `PEC`（完纯导体）。
> 35μm 铜厚在微波频段（<20GHz）趋肤深度 ~1μm，可近似为 PEC。

## 四、介质材料 (common_dielectrics.json)

| 材料 | εr | tanδ | 用途 |
|------|-----|------|------|
| Air | 1.00 | 0 | 空气 |
| Teflon (PTFE) | 2.10 | 0.0002 | 极低损耗 |
| Polyethylene | 2.25 | 0.0005 | 聚乙烯 |
| Polystyrene | 2.56 | 0.0003 | 聚苯乙烯 |
| Quartz | 3.78 | 0.0001 | 石英 |
| Sapphire | 9.40 | 0.0001 | 蓝宝石 |
| Silicon | 11.70 | 0.0001 | 硅 |
| Gallium Arsenide | 12.90 | 0.0006 | 砷化镓 |
| Alumina (Al2O3) | 9.80 | 0.0003 | 氧化铝陶瓷 |
| Glass (Pyrex) | 4.82 | 0.0054 | 玻璃 |

## 五、在脚本中使用

### 方法1：直接定义（推荐，简单）
```python
m3d.add_to_history("mat_ro4003c", """
With Material
  .Reset
  .Name "RO4003C"
  .FrqType "Frequency independent"
  .Type "Normal"
  .Epsilon "3.55"
  .TanD "0.0027"
  .TanDFreq "0"
  .Create
End With
""")
```

### 方法2：从 JSON 读取
```python
import json
with open("data/substrates.json") as f:
    substrates = json.load(f)

mat = substrates["RO4003C"]
print(f"εr={mat['epsilon_r']}, tanδ={mat['loss_tangent']}")
```

### 方法3：用 CST 内置材料库
CST 自带完整材料库，建模时直接引用名称即可：
```python
# 铜直接用内置
.Range ... .Material "Copper (annealed)"
```

## 六、吸波超材料典型材料配置

| 层 | 材料 | εr | tanδ | 厚度 |
|----|------|-----|------|------|
| 顶层图案 | Copper (annealed) | — | — | 0.035mm |
| 介质 | RO4003C | 3.55 | 0.0027 | 1.524mm |
| 背板 | Copper (annealed) | — | — | 0.035mm |

> 铜层在 2-18GHz 趋肤深度 < 1μm，35μm 厚度足够，可近似 PEC。
