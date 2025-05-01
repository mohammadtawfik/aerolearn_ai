from app.core.prompts.optimizers import PromptOptimizer

def test_no_optimization_by_default():
    opt = PromptOptimizer()
    inp = "Keep exactly."
    out = opt.optimize(inp)
    assert out == inp

def test_shortening_applies_if_context_requests():
    opt = PromptOptimizer()
    long = "x" * 2001
    out = opt.optimize(long, context={"minimize_length": True})
    assert out.endswith("...") and len(out) <= 1003

def test_no_shortening_if_length_ok():
    opt = PromptOptimizer()
    short = "A nice short prompt"
    out = opt.optimize(short, context={"minimize_length": True})
    assert out == short