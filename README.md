# Pokemon SV Damage Calculator MCP

ポケモンSVのダメージ計算MCPサーバ

ポケモン名・技名等の入力は日本語をベースとしています。

## ✨ 主な機能

### 🎯 高精度ダメージ計算
- **16段階乱数ロール** (85%-100%) による正確なダメージ範囲計算
- **確定x発計算**: 最小ダメージベースで100%確実にKOできる攻撃回数
- **乱数x発分析**: 確定x発未満での各攻撃回数でのKO確率
- タイプ相性、テラスタル対応
- 天気・フィールド効果のサポート

## 🚀 クイックスタート

### 必要要件
- Python 3.12+

### インストール
```bash
git clone https://github.com/your-username/pokemon_sv_damage_calc_mcp.git
cd pokemon_sv_damage_calc_mcp
poetry install
```

### MCPサーバー起動

```bash
poetry run python src/pokemon_damage_fastmcp_server.py
```

Claude Desktop で用いる際は

```
docker build -t pokemon-damage-mcp .
```

でイメージをビルドした後、以下のように設定してください。

```json
{
  "mcpServers": {
    "pokemon_damage_fastmcp_server": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network",
        "host",
        "pokemon-damage-mcp"
      ]
    }
  }
}

```

## 📖 使用方法

### 基本的なダメージ計算

```python
# MCPツール呼び出し例
calculate_damage(
    attacker={
        "species": "ガブリアス",
        "ability": "さめはだ",
        "evs": {"attack": 252, "speed": 252, "hp": 4},
        "nature": "いじっぱり",
        "item": "こだわりハチマキ"
    },
    defender={
        "species": "テツノワダチ",
        "evs": {"hp": 252, "defense": 252, "sp_defense": 4},
        "nature": "わんぱく"
    },
    move={
        "name": "じしん",
        "is_critical": False
    }
)
```

### 返り値の例

```json
{
    "move_name": "じしん",
    "min_damage": 150,
    "max_damage": 177,
    "average_damage": 163.5,
    "ko_probability": 0.0,
    "guaranteed_ko_hits": 2,
    "probable_ko_analysis": {},
    "calculation_details": {
        "type_effectiveness": 1.0,
        "stab_modifier": 1.5,
        "power": 100,
        "weather": "normal"
    }
}
```

### 🎯 確定x発・乱数x発の見方

- **`guaranteed_ko_hits: 2`** → **確定2発**: 最小ダメージでも2回攻撃すれば100%KO
- **`probable_ko_analysis: {"1": 0.125}`** → **乱数1発**: 1回攻撃で12.5%の確率でKO

### 複数技比較

```python
compare_moves(
    attacker=attacker_data,
    defender=defender_data,
    moves=[
        {"name": "じしん"},
        {"name": "ドラゴンクロー"},
        {"name": "ストーンエッジ", "is_critical": True}
    ]
)
```

## 🛠️ 利用可能なMCPツール

| ツール名 | 説明 | 主な返り値 |
|---------|------|-----------|
| `calculate_damage` | 単一技のダメージ計算 | ダメージ範囲、確定x発、乱数x発分析 |
| `compare_moves` | 複数技の比較 | 技別ダメージとおすすめ技 |
| `analyze_damage_range` | 詳細ダメージ分析 | ダメージ分布、確定数分析 |
| `search_pokemon` | ポケモン検索 | マッチするポケモンリスト |
| `get_pokemon_info` | ポケモン詳細取得 | 種族値、タイプ、特性一覧 |
| `search_moves` | 技検索 | マッチする技リスト |
| `get_move_info` | 技詳細取得 | 威力、命中率、分類等 |
| `search_items` | アイテム検索 | マッチするアイテムリスト |
| `get_item_info` | アイテム詳細取得 | 効果、威力補正等 |
| `get_type_effectiveness` | タイプ相性計算 | 倍率と効果説明 |

## 🎯 活用例

### ダメージ計算の確認
```
ガブリアス@こだわりハチマキ じしん → テツノワダチ
ダメージ: 150-177 (確定2発)
```

### 乱数調整の参考
```
フリーザー ふぶき → テツノワダチ
ダメージ: 103-121
確定2発 (乱数1発: 0%)
```

### 技選択の最適化
```
技比較結果:
1. じしん: 平均163.5ダメージ (推奨)
2. ドラゴンクロー: 平均145.2ダメージ
3. ストーンエッジ: 平均134.8ダメージ
```

## 📁 プロジェクト構造

```
pokemon_sv_damage_calc_mcp/
├── src/
│   ├── damage_calculator_api/
│   │   ├── calculators/          # 計算エンジン
│   │   │   ├── damage_calculator.py   # メイン計算機
│   │   │   ├── stat_calculator.py     # 能力値計算
│   │   │   └── type_calculator.py     # タイプ相性
│   │   ├── models/               # データモデル
│   │   │   └── pokemon_models.py      # ポケモン関連クラス
│   │   └── utils/                # ユーティリティ
│   │       └── data_loader.py          # ゲームデータ読み込み
│   ├── pokemon_damage_fastmcp_server.py # MCPサーバー
│   └── main.py                   # FastAPI アプリケーション
├── data/                         # ゲームデータ
│   ├── zukan.txt                # ポケモン種族データ
│   ├── move.txt                 # 技データ
│   └── ...
├── tests/                        # テストコード
└── README.md
```

## 🤝 Contribution

プルリクエストやイシューを歓迎します！特に以下の改善点があれば：

- 新しい特性・アイテム効果の追加
- 計算精度の向上
- バグ修正・パフォーマンス改善
- ドキュメントの改善

## 📄 ライセンス

MIT License

## 🙏 謝辞

ポケモンSVのダメージ計算仕様や各種データの調査・検証に協力いただいたコミュニティの皆様に感謝いたします。

---

**注意**: このツールは競技用途・学習目的で作成されており、公式のポケモンゲームとは関係ありません。
