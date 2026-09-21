"""
Task 1: AI Technique Decision Engine
--------------------------------------
Recommends the most suitable AI technique - Prompt Engineering, RAG, or
Fine-Tuning - for a food delivery use-case based on four input criteria.
"""


def recommend_technique(update_frequency, data_in_external_docs,
                         needs_custom_behaviour, latency_budget):
    """
    Recommend an AI technique for a food-delivery use-case.

    Parameters
    ----------
    update_frequency : str
        'high' -> underlying information/knowledge changes often
        'low'  -> underlying information/knowledge is fairly stable
    data_in_external_docs : str
        'yes' -> answer depends on external documents/knowledge base
        'no'  -> answer does not depend on external documents
    needs_custom_behaviour : str
        'yes' -> needs a specific tone/style/reasoning pattern baked in
        'no'  -> generic behaviour is acceptable
    latency_budget : str
        'low'  -> response must be fast (tight latency budget)
        'high' -> some extra latency/training time is acceptable

    Returns
    -------
    dict with keys 'technique' and 'justification'
    """

    # Normalise inputs so the function is not case-sensitive
    update_frequency = update_frequency.strip().lower()
    data_in_external_docs = data_in_external_docs.strip().lower()
    needs_custom_behaviour = needs_custom_behaviour.strip().lower()
    latency_budget = latency_budget.strip().lower()

    valid = {'high', 'low'}, {'yes', 'no'}, {'yes', 'no'}, {'low', 'high'}
    inputs = (update_frequency, data_in_external_docs,
              needs_custom_behaviour, latency_budget)
    for value, allowed in zip(inputs, valid):
        if value not in allowed:
            raise ValueError(
                f"Invalid input '{value}'. Expected one of {allowed}."
            )

    # ---------------- Decision tree ----------------

    # Rule 1: Stable knowledge + must behave in a very specific custom way
    # + latency budget can absorb the extra inference/training cost
    # -> Fine-Tuning bakes the behaviour directly into the model.
    if (needs_custom_behaviour == 'yes' and update_frequency == 'low'
            and latency_budget == 'high'):
        return {
            'technique': 'Fine-Tuning',
            'justification': (
                "The required behaviour is highly custom and the underlying "
                "knowledge rarely changes, so training it directly into the "
                "model is worthwhile. Because the latency budget is relaxed, "
                "the upfront training cost is an acceptable trade-off for "
                "consistent, specialised outputs."
            )
        }

    # Rule 2: Custom behaviour needed but knowledge changes frequently
    # -> Fine-tuning would go stale fast, so RAG + custom prompting is
    #    safer; we lean towards RAG since freshness dominates.
    if (needs_custom_behaviour == 'yes' and data_in_external_docs == 'yes'
            and update_frequency == 'high'):
        return {
            'technique': 'RAG',
            'justification': (
                "The information source changes frequently, so a fine-tuned "
                "model would quickly become outdated and expensive to "
                "retrain. Retrieval keeps answers grounded in the latest "
                "external documents while custom instructions can still be "
                "layered on through the prompt."
            )
        }

    # Rule 3: Answer depends on external documents and updates are frequent
    # -> RAG keeps the model grounded in fresh, external knowledge.
    if data_in_external_docs == 'yes' and update_frequency == 'high':
        return {
            'technique': 'RAG',
            'justification': (
                "Since the relevant knowledge lives in external documents "
                "that change often, retrieval-augmented generation can pull "
                "the latest content at query time. This avoids the cost and "
                "delay of continuously retraining a model."
            )
        }

    # Rule 4: Answer depends on external documents, no special custom
    # behaviour needed, and speed matters
    # -> RAG with a lightweight retriever satisfies both grounding and speed.
    if (data_in_external_docs == 'yes' and needs_custom_behaviour == 'no'
            and latency_budget == 'low'):
        return {
            'technique': 'RAG',
            'justification': (
                "The task needs facts sourced from external documents but "
                "no specialised behaviour, so a retrieval step combined "
                "with a general-purpose model is sufficient. This keeps "
                "responses accurate and fast without the overhead of "
                "fine-tuning."
            )
        }

    # Rule 5: No external documents needed, no custom behaviour, stable
    # task -> Prompt Engineering is the simplest, cheapest solution.
    if (data_in_external_docs == 'no' and needs_custom_behaviour == 'no'
            and update_frequency == 'low'):
        return {
            'technique': 'Prompt Engineering',
            'justification': (
                "The task does not rely on external knowledge or specialised "
                "behaviour, and requirements are stable, so a well-crafted "
                "prompt on a general-purpose model is enough. This avoids "
                "unnecessary infrastructure and training costs."
            )
        }

    # Rule 6: No external documents needed and latency must be low
    # -> Prompt Engineering is fastest since there is no retrieval or
    #    training step in the loop.
    if data_in_external_docs == 'no' and latency_budget == 'low':
        return {
            'technique': 'Prompt Engineering',
            'justification': (
                "With no dependency on external documents, a direct prompt "
                "to the model avoids the extra latency a retrieval step "
                "would add. This makes prompt engineering the most suitable "
                "choice when a fast response is required."
            )
        }

    # Rule 7: Custom behaviour required, no external documents, but latency
    # budget is tight -> fine-tuning offers custom behaviour without a
    # runtime retrieval/prompt-construction overhead.
    if (needs_custom_behaviour == 'yes' and data_in_external_docs == 'no'
            and latency_budget == 'low'):
        return {
            'technique': 'Fine-Tuning',
            'justification': (
                "The use-case needs consistent custom behaviour and has no "
                "external document dependency, but the latency budget is "
                "tight. A fine-tuned model responds quickly at inference "
                "time because the specialised behaviour is already baked "
                "in, unlike prompt engineering which needs longer, more "
                "detailed instructions."
            )
        }

    # Fallback / default rule: when no other rule matches, Prompt
    # Engineering is the lowest-cost, fastest-to-implement default.
    return {
        'technique': 'Prompt Engineering',
        'justification': (
            "No stronger signal for retrieval or fine-tuning was present in "
            "the given criteria, so the default, lowest-overhead approach is "
            "recommended. Prompt engineering can be implemented immediately "
            "and adjusted later if requirements change."
        )
    }


if __name__ == "__main__":
    scenarios = [
        {
            "name": "Real-time menu recommendations",
            "update_frequency": "high",
            "data_in_external_docs": "yes",
            "needs_custom_behaviour": "no",
            "latency_budget": "low",
        },
        {
            "name": "Complaint categorisation",
            "update_frequency": "low",
            "data_in_external_docs": "no",
            "needs_custom_behaviour": "yes",
            "latency_budget": "high",
        },
        {
            "name": "Order confirmation message generation",
            "update_frequency": "low",
            "data_in_external_docs": "no",
            "needs_custom_behaviour": "no",
            "latency_budget": "low",
        },
        {
            "name": "Domain-specific FAQ answering",
            "update_frequency": "high",
            "data_in_external_docs": "yes",
            "needs_custom_behaviour": "no",
            "latency_budget": "high",
        },
    ]

    for scenario in scenarios:
        name = scenario.pop("name")
        result = recommend_technique(**scenario)
        print(f"Scenario: {name}")
        print(f"  Inputs        : {scenario}")
        print(f"  Technique     : {result['technique']}")
        print(f"  Justification : {result['justification']}")
        print("-" * 80)
