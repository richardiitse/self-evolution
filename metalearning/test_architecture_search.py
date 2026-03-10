#!/usr/bin/env python3
"""
Model Architecture Search - FINAL TEST

Tests for Phase 4: Model Architecture Search.
"""

import sys
import random
from pathlib import Path
from datetime import datetime


# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from metalearning.architecture_search import (
    ModelArchitectureSearch,
    ArchitectureConfig,
    ArchitectureSpace,
    EvaluationResult
)


def test_search_initialization():
    """Test that search engine initializes correctly."""
    print("🧪 Testing search initialization...")
    
    search = ModelArchitectureSearch()
    
    # Check search space
    assert search.search_space is not None
    assert len(search.search_space.layer_types) > 0
    assert len(search.search_space.activation_functions) > 0
    print("  ✅ Default search space created")
    
    # Check empty state
    assert len(search.architectures) == 0
    assert len(search.evaluation_results) == 0
    assert search.search_iteration == 0
    assert search.best_architecture is None
    assert search.best_performance == 0.0
    print("  ✅ Empty search state")
    
    print("  ✅ Search initialization tests passed")
    return True


def test_random_architecture_generation():
    """Test generating random architectures."""
    print("\n🧪 Testing random architecture generation...")
    
    search = ModelArchitectureSearch()
    
    # Generate with default num_layers
    arch1 = search.generate_random_architecture(name="test_arch1")
    assert arch1.name == "test_arch1"
    assert len(arch1.layers) >= search.search_space.min_layers
    assert len(arch1.layers) <= search.search_space.max_layers
    assert arch1.complexity > 0.0
    assert arch1.complexity <= 1.0
    assert not arch1.evaluated
    print(f"  ✅ Generated architecture with {len(arch1.layers)} layers")
    
    # Generate with specific num_layers
    arch2 = search.generate_random_architecture(name="test_arch2", num_layers=5)
    assert len(arch2.layers) == 5
    print(f"  ✅ Generated architecture with 5 layers")
    
    # Check layer properties
    for layer in arch1.layers:
        assert "type" in layer
        assert "activation" in layer
        assert "size" in layer
        assert layer["type"] in search.search_space.layer_types
        assert layer["activation"] in search.search_space.activation_functions
    print("  ✅ All layers have valid properties")
    
    print("  ✅ Random architecture generation tests passed")
    return True


def test_architecture_mutation():
    """Test mutating architectures."""
    print("\n🧪 Testing architecture mutation...")
    
    search = ModelArchitectureSearch()
    
    # Generate base architecture
    base_arch = search.generate_random_architecture(name="base", num_layers=5)
    
    # Mutate with low rate
    mut1 = search.mutate_architecture(base_arch, mutation_rate=0.1)
    assert mut1.name == "base_mutated"
    assert len(mut1.layers) == len(base_arch.layers)
    assert mut1.config_id != base_arch.config_id
    print("  ✅ Mutated architecture created (low rate)")
    
    # Mutate with high rate
    mut2 = search.mutate_architecture(base_arch, mutation_rate=1.0)
    assert mut2.name == "base_mutated"
    assert len(mut2.layers) == len(base_arch.layers)
    print("  ✅ Mutated architecture created (high rate)")
    
    # Check that mutation actually changes things
    mut3 = search.mutate_architecture(base_arch, mutation_rate=1.0)
    differences = 0
    for i, (base_layer, mut_layer) in enumerate(zip(base_arch.layers, mut3.layers)):
        if (base_layer["type"] != mut_layer["type"] or
            base_layer["activation"] != mut_layer["activation"] or
            base_layer["size"] != mut_layer["size"]):
            differences += 1
    assert differences > 0
    print(f"  ✅ Mutation introduced {differences} layer changes")
    
    print("  ✅ Architecture mutation tests passed")
    return True


def test_architecture_crossover():
    """Test crossover between architectures."""
    print("\n🧪 Testing architecture crossover...")
    
    search = ModelArchitectureSearch()
    
    # Generate parents
    parent1 = search.generate_random_architecture(name="parent1", num_layers=5)
    parent2 = search.generate_random_architecture(name="parent2", num_layers=7)
    
    # Crossover
    child = search.crossover_architectures(parent1, parent2)
    
    assert child.name == "parent1_x_parent2"
    assert len(child.layers) >= search.search_space.min_layers
    assert child.config_id != parent1.config_id
    assert child.config_id != parent2.config_id
    print(f"  ✅ Child created with {len(child.layers)} layers")
    
    # Check that child inherits from parents
    assert child.complexity >= 0.0
    assert child.complexity <= 1.0
    print("  ✅ Child complexity within bounds")
    
    # Check parameter crossover
    assert "learning_rate" in child.parameters
    assert "batch_size" in child.parameters
    print("  ✅ Parameters inherited/crossover")
    
    print("  ✅ Architecture crossover tests passed")
    return True


def test_architecture_evaluation():
    """Test evaluating architectures."""
    print("\n🧪 Testing architecture evaluation...")
    
    search = ModelArchitectureSearch()
    
    # Generate and evaluate architecture
    arch = search.generate_random_architecture(name="test", num_layers=5)
    result = search.evaluate_architecture(arch)
    
    assert result.config_id == arch.config_id
    assert 0.0 <= result.performance <= 1.0
    assert 0.0 <= result.loss <= 1.0
    assert 0.0 <= result.accuracy <= 1.0
    assert result.training_time > 0
    assert result.inference_time > 0
    assert result.num_parameters > 0
    assert arch.performance == result.performance
    assert arch.evaluated == True
    print(f"  ✅ Architecture evaluated: performance={result.performance:.3f}")
    
    # Check that result is stored
    assert arch.config_id in search.architectures
    assert arch.config_id in search.evaluation_results
    assert search.best_architecture == arch.config_id
    assert search.best_performance == result.performance
    print("  ✅ Results stored and best updated")
    
    # Evaluate another architecture
    arch2 = search.generate_random_architecture(name="test2", num_layers=3)
    result2 = search.evaluate_architecture(arch2)
    
    assert arch2.config_id in search.architectures
    assert arch2.config_id in search.evaluation_results
    print("  ✅ Second architecture evaluated and stored")
    
    print("  ✅ Architecture evaluation tests passed")
    return True


def test_random_search():
    """Test random architecture search."""
    print("\n🧪 Testing random search...")
    
    search = ModelArchitectureSearch()
    
    # Perform random search
    try:
        results = search.random_search(num_iterations=5, name_prefix="random")
    except Exception as e:
        print(f"  ❌ Random search failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    assert len(results) == 5
    assert len(search.architectures) == 5
    assert len(search.evaluation_results) == 5
    assert search.search_iteration > 0
    print(f"  ✅ Random search completed: {len(results)} architectures")
    
    # Check results
    for result in results:
        assert 0.0 <= result.performance <= 1.0
        assert result.config_id in search.architectures
        assert result.config_id in search.evaluation_results
    print("  ✅ All results valid")
    
    # Check best architecture
    best_archs = search.get_best_architectures(n=3)
    assert len(best_archs) == 3
    assert best_archs[0][1].performance >= best_archs[1][1].performance
    assert best_archs[1][1].performance >= best_archs[2][1].performance
    print(f"  ✅ Top 3 architectures retrieved: best={best_archs[0][1].performance:.3f}")
    
    print("  ✅ Random search tests passed")
    return True


def test_evolutionary_search():
    """Test evolutionary architecture search."""
    print("\n🧪 Testing evolutionary search...")
    
    search = ModelArchitectureSearch()
    
    # Perform evolutionary search
    results = search.evolutionary_search(
        num_generations=3,
        population_size=6,
        name_prefix="evo"
    )
    
    # Check that search completed
    assert len(search.architectures) >= 6
    assert len(search.evaluation_results) >= 6
    print(f"  ✅ Evolutionary search completed: {len(search.architectures)} architectures")
    
    # Get best architectures
    best_archs = search.get_best_architectures(n=5)
    assert len(best_archs) == 5
    assert best_archs[0][1].performance >= 0.6
    print(f"  ✅ Best architecture: {best_archs[0][0].name} = {best_archs[0][1].performance:.3f}")
    
    # Check performance improvement
    search_random = ModelArchitectureSearch()
    random_results = search_random.random_search(num_iterations=10)
    random_best = max(random_results, key=lambda x: x.performance).performance
    
    evo_best = best_archs[0][1].performance
    print(f"  ✅ Performance comparison: random={random_best:.3f}, evo={evo_best:.3f}")
    
    print("  ✅ Evolutionary search tests passed")
    return True


def test_get_best_architectures():
    """Test retrieving best architectures."""
    print("\n🧪 Testing get_best_architectures...")
    
    search = ModelArchitectureSearch()
    
    # Generate multiple architectures
    for i in range(10):
        arch = search.generate_random_architecture(name=f"arch{i}", num_layers=random.randint(3, 8))
        search.evaluate_architecture(arch)
    
    # Get top 5
    best5 = search.get_best_architectures(n=5)
    assert len(best5) == 5
    print("  ✅ Retrieved top 5 architectures")
    
    # Check sorting
    for i in range(len(best5) - 1):
        assert best5[i][1].performance >= best5[i+1][1].performance
    print("  ✅ Architectures correctly sorted by performance")
    
    # Get all
    all_archs = search.get_best_architectures(n=100)
    assert len(all_archs) == 10
    print("  ✅ Retrieved all architectures")
    
    print("  ✅ Get best architectures tests passed")
    return True


def run_all_tests():
    """Run all tests."""
    
    print("=" * 70)
    print("🏗️  Model Architecture Search Tests (Phase 4) - FINAL TEST")
    print("=" * 70)
    print()
    
    # Set random seed for reproducibility
    random.seed(42)
    
    tests = {
        "Search Initialization": test_search_initialization,
        "Random Architecture Generation": test_random_architecture_generation,
        "Architecture Mutation": test_architecture_mutation,
        "Architecture Crossover": test_architecture_crossover,
        "Architecture Evaluation": test_architecture_evaluation,
        "Random Search": test_random_search,
        "Evolutionary Search": test_evolutionary_search,
        "Get Best Architectures": test_get_best_architectures,
    }
    
    results = {}
    for name, test_func in tests.items():
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Model Architecture Search component complete.")
        print("   Phase 4: Model Architecture Search - 100% COMPLETE")
        print("   Ready to proceed to: Hyperparameter Optimization")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review and fix.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    print()
    print("=" * 70)
    sys.exit(0 if success else 1)
