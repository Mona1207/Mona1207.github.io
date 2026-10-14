"""Explicit, independently derived questions. No parameter-variant generation."""
QUESTIONS = []


def Q(point, method, prompt, choices, reason, level=2, check=None):
    assert len(choices) == 4 and len(set(choices)) == 4, (point, method)
    assert len(prompt) >= 28 and any(x in prompt for x in ['？', '求', '判断']), (point, method)
    assert len(reason) >= 24, (point, method)
    QUESTIONS.append(dict(point='DM-K'+point, method=method, prompt=prompt,
                          choices=choices, reason=reason, level=level, check=check))
