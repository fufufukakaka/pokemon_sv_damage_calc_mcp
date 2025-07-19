# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Pokémon Scarlet/Violet (SV) damage calculation API built with FastAPI. It provides high-precision damage calculations for competitive Pokémon battling, supporting 16-stage random damage rolls, comprehensive stat calculations, type effectiveness (including Terastal mechanics), abilities, items, weather, and terrain effects.

## Common Development Commands

### Running the Application
```bash
# Development server with auto-reload
python src/damage_calculator_api/main.py

# Production server with uvicorn
uvicorn src.damage_calculator_api.main:app --host 0.0.0.0 --port 8000

# Install dependencies
pip install -e .
# or with Poetry (if available)
poetry install
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_calculators/test_damage_calculator.py -v

# Run tests with detailed output
python tests/test_calculators/test_damage_calculator.py
```

### Development Tools
```bash
# Check for linting/typing issues (if available)
python -m pytest tests/ --verbose

# Access interactive API documentation
# Start the server and visit: http://localhost:8000/docs
```

## Architecture Overview

### Core Components

**FastAPI Application** (`src/damage_calculator_api/main.py`)
- Main application entry point with CORS, exception handling, and router registration
- Lifespan management for data preloading
- Health check and documentation endpoints

**Damage Calculation Engine** (`src/damage_calculator_api/calculators/damage_calculator.py`)
- `DamageCalculator`: Main calculation engine integrating all mechanics
- Supports 16-stage damage rolls (85%-100% random factor)
- Comprehensive ability, item, weather, terrain, and status effect handling
- Move comparison and detailed analysis capabilities

**Data Models** (`src/damage_calculator_api/models/pokemon_models.py`)
- `PokemonState`: Complete Pokémon battle state (stats, abilities, conditions)
- `MoveInput`: Move information with modifiers
- `BattleConditions`: Field conditions (weather, terrain, room effects)
- `DamageResult`: Comprehensive calculation results with KO analysis

**Type System** (`src/damage_calculator_api/calculators/type_calculator.py`)
- Type effectiveness calculations including Terastal mechanics
- STAB (Same Type Attack Bonus) calculations

**Stat Calculations** (`src/damage_calculator_api/calculators/stat_calculator.py`)
- Real stat calculation from base stats, EVs, IVs, nature
- Ability and item modifiers for attack/defense stats
- Move power calculations with various modifiers

### API Structure

**Router Organization**:
- `/api/v1/damage/*` - Damage calculation endpoints
- `/api/v1/pokemon/*` - Pokémon information endpoints  
- `/api/v1/info/*` - General game data endpoints

**Key Endpoints**:
- `POST /api/v1/damage/calculate` - Single damage calculation
- `POST /api/v1/damage/compare` - Compare multiple moves
- `POST /api/v1/damage/analyze` - Detailed damage range analysis

### Data Loading

**Game Data** (`data/` directory):
- Pokémon species data (`zukan.txt`)
- Move data (`move.txt`) 
- Type effectiveness (`type.txt`)
- Abilities, items, natures, and other game data
- Data is preloaded on application startup for performance

**Data Loader** (`src/damage_calculator_api/utils/data_loader.py`):
- Singleton pattern for game data access
- Efficient lookup methods for Pokémon, moves, and items
- Japanese game data support

### Testing Strategy

**Comprehensive Test Suite** (`tests/test_calculators/test_damage_calculator.py`):
- Basic mechanics: type effectiveness, STAB, critical hits, weather
- Status effects: burn, paralysis, etc.
- Ability testing: 50+ abilities with specific test cases
- Integration tests with actual Pokémon battle scenarios
- Compatibility tests with external damage calculators

## Key Implementation Details

### Damage Calculation Formula
```
Base Damage = ((Level * 0.4 + 2) * Power * Attack / Defense) / 50 + 2
Final Damage = Base Damage * [Type Effectiveness] * [STAB] * [Ability/Item/Weather Modifiers] * [Critical Hit] * [Random Factor 85%-100%]
```

### Special Mechanics Support
- **Terastal**: Type changes and STAB modifications
- **Paradox Abilities**: Quark Charge and Protosynthesis stat boosts
- **Complex Abilities**: Supreme Overlord, Rivalry, Analytic with conditional effects
- **Weather/Terrain**: All SV weather and terrain effects
- **Status Effects**: Burn, paralysis, and other conditions

### Helper Functions
- `create_simple_pokemon()`: Quick Pokémon creation with EVs/IVs calculation
- Move and Pokémon validation functions
- Extensive ability effect implementations

## Development Notes

- The codebase uses dataclasses extensively for type safety
- All Japanese game data is supported natively
- Comprehensive logging for debugging calculation issues
- Modular design allows easy addition of new abilities and mechanics
- API responses include detailed calculation breakdowns for transparency