"""Stage 3b — tag: heuristic chapter classification + difficulty estimate.

HEURISTIC, NOT AUTHORITATIVE. Every output carries ``"heuristic": True`` and
``"needs_review": True``: a human (or a stronger classifier later) must
confirm chapters and difficulty before publishing. The keyword lists below
are a starting point, not a syllabus.

- :func:`classify_chapters` — keyword scoring per subject; returns chapters
  ordered by score (empty when the text is empty or nothing matches).
- :func:`heuristic_difficulty` — qtype baseline adjusted by text length and
  complexity cues.
- :func:`tag` — convenience wrapper producing the ``taxonomy``-shaped dict
  plus review flags.
"""

import re

# chapter -> keywords (matched case-insensitively on word boundaries)
CHAPTERS: dict[str, list[tuple[str, list[str]]]] = {
    "physics": [
        ("Kinematics", ["projectile", "kinematics", "velocity", "acceleration",
                         "relative velocity", "motion in a plane"]),
        ("Laws of Motion", ["friction", "newton", "inertia", "tension",
                             "pseudo force", "constraint"]),
        ("Work, Energy and Power", ["work", "kinetic energy", "potential energy",
                                    "power", "work-energy theorem", "conservative"]),
        ("Rotational Mechanics", ["torque", "moment of inertia", "angular momentum",
                                  "rolling", "rotational"]),
        ("Gravitation", ["gravitation", "escape velocity", "satellite",
                         "kepler", "gravitational"]),
        ("Fluids and Properties of Matter", ["viscosity", "surface tension",
                                             "bernoulli", "buoyant", "elasticity",
                                             "strain", "stress"]),
        ("Thermodynamics and KTG", ["thermodynamics", "carnot", "entropy",
                                    "adiabatic", "isothermal", "kinetic theory"]),
        ("SHM and Waves", ["shm", "simple harmonic", "pendulum", "standing wave",
                           "doppler", "resonance", "wave equation"]),
        ("Electrostatics", ["coulomb", "electric field", "potential",
                            "capacitor", "gauss", "dipole"]),
        ("Current Electricity", ["resistance", "kirchhoff", "wheatstone",
                                 "potentiometer", "drift velocity", "ohm"]),
        ("Magnetism", ["magnetic field", "ampere", "lorentz", "cyclotron",
                       "solenoid", "magnet"]),
        ("EMI and AC", ["induction", "lenz", "inductance", "reactance",
                        "transformer", "alternating current"]),
        ("Ray Optics", ["mirror", "lens", "refraction", "total internal reflection",
                        "prism", "focal length"]),
        ("Wave Optics", ["interference", "diffraction", "polarisation",
                         "polarization", "young", "fringe"]),
        ("Modern Physics", ["photoelectric", "de broglie", "bohr", "x-ray",
                            "radioactiv", "nucleus", "binding energy"]),
        ("Semiconductors", ["semiconductor", "diode", "transistor", "logic gate",
                            "zener"]),
    ],
    "chemistry": [
        ("Mole Concept", ["mole", "stoichiometry", "limiting reagent",
                          "percentage composition", "empirical formula"]),
        ("Atomic Structure", ["quantum", "orbital", "aufbau", "heisenberg",
                              "photoelectric", "spectrum", "bohr"]),
        ("Chemical Bonding", ["hybridisation", "hybridization", "vsepr",
                              "molecular orbital", "bond order", "fajan"]),
        ("Thermodynamics", ["enthalpy", "entropy", "gibbs", "hess",
                            "spontaneous", "thermochemistry"]),
        ("Chemical Equilibrium", ["equilibrium constant", "le chatelier",
                                  "kp", "kc"]),
        ("Ionic Equilibrium", ["ph ", "buffer", "solubility product",
                               "titration", "indicator", "hydrolysis"]),
        ("Electrochemistry", ["electrolysis", "nernst", "cell", "emf",
                              "faraday", "conductance"]),
        ("Chemical Kinetics", ["rate", "order of reaction", "half-life",
                               "arrhenius", "catalyst"]),
        ("s-Block Elements", ["alkali", "alkaline earth"]),
        ("p-Block Elements", ["boron", "carbon family", "nitrogen family",
                              "oxygen family", "halogen", "noble gas"]),
        ("d- and f-Block Elements", ["transition", "lanthanide", "actinide"]),
        ("Coordination Compounds", ["ligand", "coordination", "crystal field",
                                    "isomerism", "edta"]),
        ("Metallurgy", ["extraction", "roasting", "calcination", "smelting",
                        "refining"]),
        ("Salt Analysis", ["salt analysis", "cation", "anion", "precipitate",
                           "flame test", "borax bead"]),
        ("GOC and Isomerism", ["resonance", "hyperconjugation", "isomer",
                               "tautomer", "chirality", "optical activity"]),
        ("Hydrocarbons", ["alkane", "alkene", "alkyne", "benzene", "aromatic",
                          "wurtz", "ozonolysis"]),
        ("Haloalkanes and Alcohols", ["haloalkane", "alcohol", "phenol",
                                      "ether", "williamson"]),
        ("Carbonyl Compounds", ["aldehyde", "ketone", "carboxylic acid",
                                "ester", "aldol", "cannizzaro"]),
        ("Amines", ["amine", "diazonium", "azo", "hoffmann"]),
        ("Biomolecules and Polymers", ["carbohydrate", "protein", "polymer",
                                       "dna", "enzyme", "nylon"]),
    ],
    "mathematics": [
        ("Sets, Relations and Functions", ["set", "relation", "function",
                                            "domain", "range", "bijective"]),
        ("Quadratic Equations", ["quadratic", "discriminant", "roots"]),
        ("Complex Numbers", ["complex", "argand", "modulus", "argument",
                             "iota", "conjugate"]),
        ("Matrices and Determinants", ["matrix", "matrices", "determinant",
                                       "inverse", "rank", "eigen"]),
        ("Permutations and Combinations", ["permutation", "combination",
                                           "factorial", "arrangement"]),
        ("Binomial Theorem", ["binomial", "pascal"]),
        ("Sequences and Series", ["arithmetic progression", "geometric progression",
                                  "harmonic", "series", "sequence", "ap ", "gp "]),
        ("Limits, Continuity and Differentiability", ["limit", "continuity",
                                                      "differentiable", "l'hospital"]),
        ("Applications of Derivatives", ["maxima", "minima", "tangent",
                                         "normal", "increasing", "decreasing",
                                         "rate of change"]),
        ("Indefinite Integration", ["indefinite integral", "integration by parts",
                                    "partial fraction"]),
        ("Definite Integration and Area", ["definite integral", "area under",
                                           "area between", "gamma"]),
        ("Differential Equations", ["differential equation", "order",
                                    "degree", "integrating factor",
                                    "variable separable"]),
        ("Straight Lines", ["straight line", "slope", "intercept"]),
        ("Circles", ["circle", "chord", "tangent to circle"]),
        ("Parabola, Ellipse and Hyperbola", ["parabola", "ellipse", "hyperbola",
                                             "focus", "directrix", "latus rectum"]),
        ("Vectors", ["vector", "dot product", "cross product", "scalar triple"]),
        ("3D Geometry", ["plane", "line in space", "direction cosine",
                        "shortest distance", "skew lines"]),
        ("Probability", ["probability", "bayes", "conditional", "dice",
                         "random variable"]),
        ("Trigonometry", ["trigonometric", "sine rule", "cosine rule",
                          "inverse trigonometric"]),
        ("Statistics", ["mean", "median", "variance", "standard deviation"]),
    ],
}

_QTYPE_BASE_DIFFICULTY = {
    "MCQ": "medium", "single_correct": "medium",
    "SA": "medium", "numerical": "medium", "stem_numerical": "hard",
    "multi_correct": "hard", "matrix_match": "hard",
}

_COMPLEXITY_CUES = [
    "assertion", "reason", "match the following", "comprehension",
    "paragraph", "statement", "two statements",
]


def _score_text(text: str, keywords: list[str]) -> int:
    score = 0
    for kw in keywords:
        pattern = r"\b" + re.escape(kw.strip()) + r"\b"
        score += len(re.findall(pattern, text, flags=re.IGNORECASE))
    return score


def classify_chapters(text: str, subject: str, top_k: int = 3) -> list[str]:
    """Keyword-score chapters for *subject*; best-first, empty if no signal."""
    if not text or not text.strip() or subject not in CHAPTERS:
        return []
    scored = [(chap, _score_text(text, kws))
              for chap, kws in CHAPTERS[subject]]
    scored = [(c, s) for c, s in scored if s > 0]
    scored.sort(key=lambda cs: (-cs[1], cs[0]))
    return [c for c, _ in scored[:top_k]]


def heuristic_difficulty(qtype: str, text: str = "") -> str:
    """Qtype baseline, bumped up by length / complexity cues. Heuristic."""
    level = _QTYPE_BASE_DIFFICULTY.get(qtype, "medium")
    order = ["easy", "medium", "hard"]
    idx = order.index(level)
    lowered = text.lower()
    if len(text) > 600 or any(cue in lowered for cue in _COMPLEXITY_CUES):
        idx = min(2, idx + 1)
    if 0 < len(text) < 120 and qtype in ("MCQ", "single_correct"):
        idx = max(0, idx - 1)
    return order[idx]


def tag(question: dict) -> dict:
    """Tag a raw/ingest record. Always heuristic; always needs review."""
    text = question.get("stem_latex") or question.get("stem_text") or ""
    subject = (question.get("subject") or "").lower()
    qtype = question.get("question_type") or question.get("qtype") or ""
    chapters = classify_chapters(text, subject)
    return {
        "chapters": chapters,
        "difficulty": heuristic_difficulty(qtype, text),
        "heuristic": True,
        "needs_review": True,
        "note": ("keyword heuristic only — confirm chapters and difficulty "
                 "before publishing"),
    }
