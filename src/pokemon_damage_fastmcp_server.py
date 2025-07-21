#!/usr/bin/env python3
"""
Pokemon SV Damage Calculator FastMCP Server

このMCPサーバーは、ポケモンSVのダメージ計算機能を
FastMCPを使用してModel Context Protocol (MCP) ツールとして提供します。

提供ツール:
- calculate_damage: ダメージ計算
- compare_moves: 技比較
- analyze_damage_range: ダメージ詳細分析
- search_pokemon: ポケモン検索
- get_pokemon_info: ポケモン詳細取得
- search_moves: 技検索
- get_move_info: 技詳細取得
- search_items: アイテム検索
- get_item_info: アイテム詳細取得
- get_type_effectiveness: タイプ相性計算
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# 既存のダメージ計算機能をインポート
from src.damage_calculator_api.calculators.damage_calculator import DamageCalculator
from src.damage_calculator_api.calculators.type_calculator import TypeCalculator
from src.damage_calculator_api.models.pokemon_models import (
    BattleConditions,
    MoveInput,
    PokemonState,
    StatusAilment,
    TerrainCondition,
    WeatherCondition,
)
from src.damage_calculator_api.utils.data_loader import get_data_loader
from src.damage_calculator_api.utils.stat_calculator import calculate_actual_stats

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pokemon-damage-fastmcp")

# FastMCPサーバー作成
mcp = FastMCP("pokemon-damage-calculator")

# グローバル変数でデータローダーと計算機を初期化
damage_calculator = None
type_calculator = None
data_loader = None


def initialize_calculators():
    """計算機とデータローダーを初期化"""
    global damage_calculator, type_calculator, data_loader
    if not damage_calculator:
        logger.info("Initializing calculators and data loader...")
        damage_calculator = DamageCalculator()
        type_calculator = TypeCalculator()
        data_loader = get_data_loader()
        logger.info(
            f"Loaded {len(data_loader.pokemon_data)} Pokemon and "
            f"{len(data_loader.move_data)} moves"
        )


@dataclass
class DamageResult:
    """ダメージ計算結果のデータクラス"""

    move_name: str
    min_damage: int
    max_damage: int
    average_damage: float
    hp_percentage_min: float
    hp_percentage_max: float
    ko_probability: float
    guaranteed_ko_hits: int
    probable_ko_analysis: Dict[int, float]
    calculation_details: Dict[str, Any]


@dataclass
class MoveComparison:
    """技比較結果のデータクラス"""

    move_name: str
    min_damage: int
    max_damage: int
    average_damage: float
    ko_probability: float


@dataclass
class ComparisonResult:
    """技比較の全体結果"""

    results: List[MoveComparison]
    recommended_move: str
    total_moves: int


@dataclass
class PokemonInfo:
    """ポケモン情報のデータクラス"""

    number: int
    name: str
    types: List[str]
    abilities: List[str]
    base_stats: Dict[str, int]
    weight: float


@dataclass
class MoveInfo:
    """技情報のデータクラス"""

    name: str
    move_type: str
    category: str
    power: int
    accuracy: int
    pp: int


@dataclass
class ItemInfo:
    """アイテム情報のデータクラス"""

    name: str
    fling_power: int
    boost_type: Optional[str]
    resist_type: Optional[str]
    power_modifier: float
    is_consumable: bool


@dataclass
class TypeEffectiveness:
    """タイプ相性のデータクラス"""

    attacking_type: str
    defending_types: List[str]
    effectiveness: float
    description: str


@dataclass
class SearchResult:
    """検索結果のデータクラス"""

    items: List[str]
    total: int
    query: str
    offset: int
    limit: int


@dataclass
class DamageAnalysis:
    """ダメージ詳細分析結果"""

    move_name: str
    min_damage: int
    max_damage: int
    average_damage: float
    damage_distribution: Dict[int, float]
    ko_analysis: Dict[str, float]


def convert_to_pokemon_state(data: Dict[str, Any]) -> PokemonState:
    """辞書データをPokemonStateに変換"""
    initialize_calculators()

    if "evs" in data and data["evs"]:
        # 努力値が指定されている場合は実数値を計算
        stats = calculate_actual_stats(
            species=data.get("species", ""),
            level=data.get("level", 50),
            evs=data.get("evs", {}),
            ivs=data.get("ivs", None),
            nature=data.get("nature", "まじめ"),
        )
    else:
        # 直接指定された実数値を使用
        stats = data.get("stats", {})

    return PokemonState(
        species=data.get("species", ""),
        level=data.get("level", 50),
        stats=stats,
        nature=data.get("nature", "まじめ"),
        ability=data.get("ability", ""),
        item=data.get("item"),
        terastal_type=data.get("terastal_type"),
        is_terastalized=data.get("is_terastalized", False),
        status_ailment=StatusAilment(data.get("status_ailment", "normal")),
        hp_ratio=data.get("hp_ratio", 1.0),
        stat_boosts=data.get("stat_boosts", {}),
        paradox_boost_stat=data.get("paradox_boost_stat"),
        gender=data.get("gender"),
        fainted_teammates=data.get("fainted_teammates", 0),
        moves_last=data.get("moves_last", False),
        flash_fire_active=data.get("flash_fire_active", False),
    )


def convert_to_move_input(data: Dict[str, Any]) -> MoveInput:
    """辞書データをMoveInputに変換"""
    return MoveInput(
        name=data.get("name", ""),
        move_type=data.get("move_type"),
        is_critical=data.get("is_critical", False),
        power_modifier=data.get("power_modifier", 1.0),
    )


def convert_to_battle_conditions(data: Dict[str, Any]) -> BattleConditions:
    """辞書データをBattleConditionsに変換"""
    return BattleConditions(
        weather=WeatherCondition(data.get("weather", "normal")),
        terrain=TerrainCondition(data.get("terrain", "normal")),
        trick_room=data.get("trick_room", False),
        gravity=data.get("gravity", False),
        magic_room=data.get("magic_room", False),
        wonder_room=data.get("wonder_room", False),
        reflect=data.get("reflect", False),
        light_screen=data.get("light_screen", False),
        aurora_veil=data.get("aurora_veil", False),
        tailwind=data.get("tailwind", False),
    )


@mcp.tool()
def calculate_damage(
    attacker: Dict[str, Any],
    defender: Dict[str, Any],
    move: Dict[str, Any],
    conditions: Optional[Dict[str, Any]] = None,
) -> DamageResult:
    """
    ポケモンのダメージを計算します

    返される結果には以下の情報が含まれます：
    - 基本ダメージ情報（最小/最大/平均）
    - 確定x発: guaranteed_ko_hits（最小ダメージベースで100%確実にKOできる回数）
    - 乱数x発: probable_ko_analysis（確定x発未満での各攻撃回数のKO確率）

    Args:
        attacker: 攻撃側ポケモンの情報
        defender: 防御側ポケモンの情報
        move: 技の情報
        conditions: バトル条件（オプション）

        情報の形式(attacker, defender):
        {
            "species": "ピカチュウ",
            "level": 50,
            "evs": {"hp": 0, "attack": 252, "defense": 0, "sp_attack": 252, "sp_defense": 0, "speed": 4},
            "ivs": {"hp": 31, "attack": 31, "defense": 31, "sp_attack": 31, "sp_defense": 31, "speed": 31},
            "nature": "いじっぱり",
            "ability": "せいでんき",
            "item": "きあいのタスキ",
            "terastal_type": "でんき",
            "is_terastalized": False,
            "status_ailment": "normal",
            "stat_boosts": {"attack": 1},
            "hp_ratio": 1.0,
        }
        moveの形式:
        {
            "name": "10まんボルト",
            "move_type": "でんき",
            "is_critical": False,
            "power_modifier": 1.0,
        }
        conditionsの形式:
        {
            "weather": "はれ",
            "terrain": "なし",
            "trick_room": False,
            "gravity": False,
            "magic_room": False,
            "wonder_room": False,
            "reflect": False,
            "light_screen": False,
            "aurora_veil": False,
            "tailwind": False,
        }

    Returns:
        DamageResult: ダメージ計算結果
    """
    initialize_calculators()

    try:
        # オブジェクトに変換
        attacker_state = convert_to_pokemon_state(attacker)
        defender_state = convert_to_pokemon_state(defender)
        move_input = convert_to_move_input(move)
        battle_conditions = convert_to_battle_conditions(conditions or {})

        # ダメージ計算実行
        result = damage_calculator.calculate_damage(
            attacker_state, defender_state, move_input, battle_conditions
        )

        return DamageResult(
            move_name=move_input.name,
            min_damage=result.min_damage,
            max_damage=result.max_damage,
            average_damage=result.average_damage,
            hp_percentage_min=min(result.damage_percentage),
            hp_percentage_max=max(result.damage_percentage),
            ko_probability=result.ko_probability,
            guaranteed_ko_hits=result.guaranteed_ko_hits,
            probable_ko_analysis=result.probable_ko_analysis,
            calculation_details=result.calculation_details,
        )

    except Exception as e:
        logger.error(f"Damage calculation error: {e}")
        raise ValueError(f"ダメージ計算中にエラーが発生しました: {str(e)}")


@mcp.tool()
def compare_moves(
    attacker: Dict[str, Any],
    defender: Dict[str, Any],
    moves: List[Dict[str, Any]],
    conditions: Optional[Dict[str, Any]] = None,
) -> ComparisonResult:
    """
    複数の技のダメージを比較します

    Args:
        attacker: 攻撃側ポケモンの情報
        defender: 防御側ポケモンの情報
        moves: 比較する技のリスト
        conditions: バトル条件（オプション）

    Returns:
        ComparisonResult: 技比較結果
    """
    initialize_calculators()

    try:
        attacker_state = convert_to_pokemon_state(attacker)
        defender_state = convert_to_pokemon_state(defender)
        battle_conditions = convert_to_battle_conditions(conditions or {})

        # 各技の計算
        results = []
        for move_data in moves:
            move_input = convert_to_move_input(move_data)
            result = damage_calculator.calculate_damage(
                attacker_state, defender_state, move_input, battle_conditions
            )
            results.append(
                MoveComparison(
                    move_name=move_input.name,
                    min_damage=result.min_damage,
                    max_damage=result.max_damage,
                    average_damage=result.average_damage,
                    ko_probability=result.ko_probability,
                )
            )

        # 平均ダメージで並び替え
        sorted_results = sorted(results, key=lambda x: x.average_damage, reverse=True)

        return ComparisonResult(
            results=sorted_results,
            recommended_move=sorted_results[0].move_name if sorted_results else "",
            total_moves=len(results),
        )

    except Exception as e:
        logger.error(f"Move comparison error: {e}")
        raise ValueError(f"技比較中にエラーが発生しました: {str(e)}")


@mcp.tool()
def search_pokemon(query: str = "", limit: int = 20, offset: int = 0) -> SearchResult:
    """
    ポケモンを検索します

    Args:
        query: 検索クエリ（オプション）
        limit: 取得件数制限（デフォルト: 20）
        offset: 取得開始位置（デフォルト: 0）

    Returns:
        SearchResult: 検索結果
    """
    initialize_calculators()

    try:
        pokemon_names = list(data_loader.pokemon_data.keys())

        # 検索フィルタリング
        if query:
            pokemon_names = [name for name in pokemon_names if query in name]

        total = len(pokemon_names)

        # ページネーション
        pokemon_names = pokemon_names[offset : offset + limit]

        return SearchResult(
            items=pokemon_names,
            total=total,
            query=query,
            offset=offset,
            limit=limit,
        )

    except Exception as e:
        logger.error(f"Pokemon search error: {e}")
        raise ValueError(f"ポケモン検索中にエラーが発生しました: {str(e)}")


@mcp.tool()
def get_pokemon_info(name: str) -> PokemonInfo:
    """
    指定されたポケモンの詳細情報を取得します

    Args:
        name: ポケモン名

    Returns:
        PokemonInfo: ポケモンの詳細情報
    """
    initialize_calculators()

    try:
        if name not in data_loader.pokemon_data:
            raise ValueError(f"ポケモン '{name}' が見つかりません")

        pokemon_data = data_loader.pokemon_data[name]

        return PokemonInfo(
            number=pokemon_data.number,
            name=name,
            types=pokemon_data.types,
            abilities=pokemon_data.abilities,
            base_stats={
                "hp": pokemon_data.hp,
                "attack": pokemon_data.attack,
                "defense": pokemon_data.defense,
                "sp_attack": pokemon_data.sp_attack,
                "sp_defense": pokemon_data.sp_defense,
                "speed": pokemon_data.speed,
            },
            weight=pokemon_data.weight,
        )

    except Exception as e:
        logger.error(f"Pokemon info error: {e}")
        raise ValueError(f"ポケモン情報取得中にエラーが発生しました: {str(e)}")


@mcp.tool()
def search_moves(
    query: str = "",
    move_type: str = "",
    limit: int = 20,
    offset: int = 0,
) -> SearchResult:
    """
    技を検索します

    Args:
        query: 検索クエリ（オプション）
        move_type: 技タイプでフィルタ（オプション）
        limit: 取得件数制限（デフォルト: 20）
        offset: 取得開始位置（デフォルト: 0）

    Returns:
        SearchResult: 検索結果
    """
    initialize_calculators()

    try:
        move_names = list(data_loader.move_data.keys())

        # 検索フィルタリング
        if query:
            move_names = [name for name in move_names if query in name]

        # タイプフィルタリング
        if move_type:
            filtered_moves = []
            for name in move_names:
                move_data = data_loader.move_data[name]
                if move_data.move_type == move_type:
                    filtered_moves.append(name)
            move_names = filtered_moves

        total = len(move_names)
        move_names = move_names[offset : offset + limit]

        return SearchResult(
            items=move_names,
            total=total,
            query=query,
            offset=offset,
            limit=limit,
        )

    except Exception as e:
        logger.error(f"Move search error: {e}")
        raise ValueError(f"技検索中にエラーが発生しました: {str(e)}")


@mcp.tool()
def get_move_info(name: str) -> MoveInfo:
    """
    指定された技の詳細情報を取得します

    Args:
        name: 技名

    Returns:
        MoveInfo: 技の詳細情報
    """
    initialize_calculators()

    try:
        if name not in data_loader.move_data:
            raise ValueError(f"技 '{name}' が見つかりません")

        move_data = data_loader.move_data[name]

        return MoveInfo(
            name=name,
            move_type=move_data.move_type,
            category=move_data.category,
            power=move_data.power,
            accuracy=move_data.accuracy,
            pp=move_data.pp,
        )

    except Exception as e:
        logger.error(f"Move info error: {e}")
        raise ValueError(f"技情報取得中にエラーが発生しました: {str(e)}")


@mcp.tool()
def search_items(query: str = "", limit: int = 20, offset: int = 0) -> SearchResult:
    """
    アイテムを検索します

    Args:
        query: 検索クエリ（オプション）
        limit: 取得件数制限（デフォルト: 20）
        offset: 取得開始位置（デフォルト: 0）

    Returns:
        SearchResult: 検索結果
    """
    initialize_calculators()

    try:
        item_names = list(data_loader.item_data.keys())

        # 検索フィルタリング
        if query:
            item_names = [name for name in item_names if query in name]

        total = len(item_names)
        item_names = item_names[offset : offset + limit]

        return SearchResult(
            items=item_names,
            total=total,
            query=query,
            offset=offset,
            limit=limit,
        )

    except Exception as e:
        logger.error(f"Item search error: {e}")
        raise ValueError(f"アイテム検索中にエラーが発生しました: {str(e)}")


@mcp.tool()
def get_item_info(name: str) -> ItemInfo:
    """
    指定されたアイテムの詳細情報を取得します

    Args:
        name: アイテム名

    Returns:
        ItemInfo: アイテムの詳細情報
    """
    initialize_calculators()

    try:
        if name not in data_loader.item_data:
            raise ValueError(f"アイテム '{name}' が見つかりません")

        item_data = data_loader.item_data[name]

        return ItemInfo(
            name=name,
            fling_power=item_data.fling_power,
            boost_type=item_data.boost_type,
            resist_type=item_data.resist_type,
            power_modifier=item_data.power_modifier,
            is_consumable=item_data.is_consumable,
        )

    except Exception as e:
        logger.error(f"Item info error: {e}")
        raise ValueError(f"アイテム情報取得中にエラーが発生しました: {str(e)}")


@mcp.tool()
def analyze_damage_range(
    attacker: Dict[str, Any],
    defender: Dict[str, Any],
    move: Dict[str, Any],
    conditions: Optional[Dict[str, Any]] = None,
) -> DamageAnalysis:
    """
    ダメージ範囲の詳細分析を行います

    Args:
        attacker: 攻撃側ポケモンの情報
        defender: 防御側ポケモンの情報
        move: 技の情報
        conditions: バトル条件（オプション）

    Returns:
        DamageAnalysis: ダメージ詳細分析結果
    """
    initialize_calculators()

    try:
        attacker_state = convert_to_pokemon_state(attacker)
        defender_state = convert_to_pokemon_state(defender)
        move_input = convert_to_move_input(move)
        battle_conditions = convert_to_battle_conditions(conditions or {})

        # ダメージ計算実行
        result = damage_calculator.calculate_damage(
            attacker_state, defender_state, move_input, battle_conditions
        )

        # ダメージ分布計算
        damage_distribution = {}
        for damage in result.damage_range:
            damage_distribution[damage] = damage_distribution.get(damage, 0) + 1

        # 確率に変換
        total_rolls = len(result.damage_range)
        for damage in damage_distribution:
            damage_distribution[damage] = damage_distribution[damage] / total_rolls

        # 確定数分析
        defender_hp = result.calculation_details.get("defender_max_hp", 100)
        ko_analysis = {}

        for hits in range(1, 6):  # 1~5確定を分析
            ko_count = sum(
                1 for damage in result.damage_range if damage * hits >= defender_hp
            )
            ko_analysis[f"{hits}確定"] = ko_count / total_rolls

        return DamageAnalysis(
            move_name=move_input.name,
            min_damage=result.min_damage,
            max_damage=result.max_damage,
            average_damage=result.average_damage,
            damage_distribution=damage_distribution,
            ko_analysis=ko_analysis,
        )

    except Exception as e:
        logger.error(f"Damage analysis error: {e}")
        raise ValueError(f"ダメージ分析中にエラーが発生しました: {str(e)}")


@mcp.tool()
def get_type_effectiveness(
    attacking_type: str, defending_types: List[str]
) -> TypeEffectiveness:
    """
    タイプ相性を計算します

    Args:
        attacking_type: 攻撃タイプ
        defending_types: 防御タイプのリスト

    Returns:
        TypeEffectiveness: タイプ相性計算結果
    """
    initialize_calculators()

    try:
        if not attacking_type or not defending_types:
            raise ValueError("攻撃タイプと防御タイプを指定してください")

        effectiveness = type_calculator.calculate_type_effectiveness(
            attacking_type, defending_types
        )

        # 相性の説明
        if effectiveness > 1.0:
            description = "効果抜群"
        elif effectiveness < 1.0:
            description = "効果いまひとつ"
        elif effectiveness == 0:
            description = "効果なし"
        else:
            description = "通常"

        return TypeEffectiveness(
            attacking_type=attacking_type,
            defending_types=defending_types,
            effectiveness=effectiveness,
            description=description,
        )

    except Exception as e:
        logger.error(f"Type effectiveness error: {e}")
        raise ValueError(f"タイプ相性計算中にエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    import sys

    # デバッグ情報を stderr に出力
    print("Starting Pokemon Damage Calculator MCP Server...", file=sys.stderr)
    print(f"Python version: {sys.version}", file=sys.stderr)
    print(f"Working directory: {os.getcwd()}", file=sys.stderr)

    try:
        # FastMCP の設定を確認
        print(
            f"MCP server configuration: {mcp}",
            file=sys.stderr,
        )

        # サーバーを起動
        mcp.run()
    except Exception as e:
        print(f"Error starting MCP server: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
