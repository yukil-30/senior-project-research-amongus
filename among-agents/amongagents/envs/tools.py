import re

import networkx as nx


class GetBestPath:
    def __init__(self, network):
        self.network = network

    def get_path(self, from_location, to_location, identity):
        """Get the quickest path to a location."""
        if identity == "Impostor":
            path = nx.shortest_path(self.network, from_location, to_location)
        else:
            path = nx.shortest_path(
                self.network, from_location, to_location, weight="weight"
            )
        path_str = "->".join(path)
        instruction = (
            "Now, write your response with [Condensed Memory], [Thinking Process], and [Action]. "
            "Make sure action is chosen from the available actions. Case sensitive."
        )
        return f"{path_str}\n{instruction}"


class AgentResponse:
    valid_actions = [
        "VOTE",
        "MOVE",
        "SPEAK",
        "CALL MEETING",
        "KILL",
        "VENT",
        "REPORT DEAD BODY",
        "VIEW MONITOR",
        "COMPLETE TASK",
        "COMPLETE FAKE TASK",
    ]

    def __init__(self, condensed_memory, thinking_process, action):
        self.condensed_memory = condensed_memory
        self.thinking_process = thinking_process
        self.action = action

        if action not in self.valid_actions:
            raise ValueError(f"Invalid action: {action}")
        
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class DecomposedUnit:
    text: str
    authority: str       # directive, informational, permissive
    risk_category: str   # high_deception_risk, medium_risk, low_risk
    attention_score: float # 0.0 - 10.0
    entities: List[str]

class EchologyAmongUsAdaptor:
    """
    Adapts echology-io/decompose architecture to evaluate Among Us observations
    deterministically via localized regex and heuristic semantic units.
    """
    
    DECEPTION_MARKERS = {
        'hedging': ['i think', 'maybe', 'could be', 'seems like', 'i guess', 'sort of'],
        'deflection': ['anyway', 'moving on', 'the point is', 'nevermind'],
        'contradiction': ['but', 'however', 'yet', 'still']
    }

    DECEPTION_MARKERS = {
        'hedging': [
            'i think', 'in my opinion', 'i believe', 'it seems', 'it appears',
            'possibly', 'arguably', 'i suppose', 'one might say', 'i guess',
            'as far as i know', 'to my knowledge', 'as i recall', 'if i remember',
            'correct me if i\'m wrong', 'i could be wrong'
        ],
        'deflection': [
            'anyway', 'regardless', 'moving on', 'back to', 'not to mention',
            "let's move past", 'that aside', 'the point is', 'the fact is',
            'bottom line', 'in any case', 'at any rate', 'in conclusion',
            'but let\'s focus on', 'nevermind that', 'never mind that'
        ],
        'contradiction': [
            'but', 'however', 'yet', 'on the other hand', 'conversely',
            'alternatively', 'meanwhile', 'then again', 'that said',
            'at the same time', 'even so', 'still', 'nonetheless', 'though'
        ],
    }

    @staticmethod
    def _classify_unit(clause: str) -> DecomposedUnit:
        clause_lower = clause.lower()
        
        # 1. Map Entity Extraction (Players & Rooms)
        players = re.findall(r'(player\s+\d+:\s+\w+|player\s+\d+)', clause_lower)
        rooms = [room for room in ['electrical', 'cafeteria', 'weapons', 'admin', 'medbay', 'security', 'navigation', 'upper engine', 'reactor', 'lower engine', 'storage', 'communications', 'shields', 'o2', ] if room in clause_lower]
        entities = list(set(players + rooms))
        
        # 2. Map Authority Level (Speech Directiveness)
        if any(w in clause_lower for w in ['vote', 'eject', 'sus', 'impostor', 'follow me']):
            authority = "directive" # Aggressive / calling shots
        elif any(w in clause_lower for w in ['was with', 'doing tasks', 'saw him']):
            authority = "informational" # Pure alibi / concrete detail
        else:
            authority = "permissive" # Passive / compliance layout

        # 3. Map Risk & Attention (Deception Mapping)
        flags = []
        for category, markers in EchologyAmongUsAdaptor.DECEPTION_MARKERS.items():
            if any(marker in clause_lower for marker in markers):
                flags.append(category)

        # Calculate attention score based on linguistic friction
        attention_score = min(10.0, len(flags) * 3.5 + (1.5 if len(clause_lower) > 60 else 0))
        
        # Categorize Deception Risk cleanly
        if attention_score >= 7.0:
            risk_category = "high_deception_risk"
        elif attention_score >= 3.5:
            risk_category = "medium_risk"
        else:
            risk_category = "low_risk"

        return DecomposedUnit(
            text=clause.strip(),
            authority=authority,
            risk_category=risk_category,
            attention_score=attention_score,
            entities=entities
        )
    
    @classmethod
    def decompose_statement(cls, statement: str) -> str:
        # Strip game-loop metadata prefixes before decomposing
        clean_statement = re.sub(
            r"(Timestep \d+:|Message:|Monitor Record:|Location:|Observation:)", "", statement
        ).strip().strip('"\'')

        if not clean_statement:
            return statement

        # Split on sentence boundaries and adversarial conjunctions only.
        # Avoid splitting on all commas — short fragments add noise without signal.
        clauses = [
            c.strip()
            for c in re.split(
                r'(?<=[.!?])\s+|,\s+(?=but|however|yet|anyway|though)',
                clean_statement,
                flags=re.IGNORECASE
            )
            if c.strip()
        ]

        units = [cls._classify_unit(clause) for clause in clauses if len(clause) > 3]

        if len(units) <= 1:
            return statement

        decomposed = "[DECOMPOSED]\n"
        for unit in units[:-1]:
            decomposed += f"  ├─ \"{unit.text}\"\n"
        decomposed += f"  └─ \"{units[-1].text}\""

        return decomposed


# class EquivocationDetector:
#     """
#     Analyzes statements (especially decomposed ones) for equivocal language patterns.
    
#     Based on research by Milkowski et al. showing that equivocation is strongly
#     associated with deceptive communication in game scenarios.
    
#     These markers can help LLMs identify potential deception when analyzing
#     decomposed statement components.
#     """
    
#     # # Equivocal language patterns - grouped by category
#     # EQUIVOCAL_MARKERS = {
#     #     'vagueness': [
#     #         'sort of', 'kind of', 'maybe', 'might', 'could be', 'seems like',
#     #         'appears to', 'arguably', 'somewhat', 'relatively', 'fairly',
#     #         'a bit', 'rather', 'quite', 'pretty', 'probably', 'perhaps',
#     #         'likely', 'apparently', 'ostensibly', 'supposedly'
#     #     ],
#     #     'hedging': [
#     #         'i think', 'in my opinion', 'i believe', 'it seems', 'it appears',
#     #         'possibly', 'arguably', 'i suppose', 'one might say', 'i guess',
#     #         'as far as i know', 'to my knowledge', 'as i recall', 'if i remember',
#     #         'correct me if i\'m wrong', 'i could be wrong'
#     #     ],
#     #     'deflection': [
#     #         'anyway', 'regardless', 'moving on', 'back to', 'not to mention',
#     #         "let's move past", 'that aside', 'the point is', 'the fact is',
#     #         'bottom line', 'in any case', 'at any rate', 'in conclusion',
#     #         'but let\'s focus on', 'nevermind that', 'never mind that'
#     #     ],
#     #     'contradiction': [
#     #         'but', 'however', 'yet', 'on the other hand', 'conversely',
#     #         'alternatively', 'meanwhile', 'then again', 'that said',
#     #         'at the same time', 'even so', 'still', 'nonetheless', 'though'
#     #     ],
#     #     'limiting_qualifiers': [
#     #         'only', 'just', 'merely', 'simply', 'alone', 'barely',
#     #         'practically', 'almost', 'nearly', 'practically', 'virtually'
#     #     ]
#     # }
    
#     @staticmethod
#     def analyze_statement(statement):
#         """
#         Analyzes a statement for equivocal markers.
#         Works with both raw and decomposed statements.
        
#         Args:
#             statement (str): Raw or decomposed statement
            
#         Returns:
#             dict: {
#                 'is_decomposed': bool,
#                 'components': list of components if decomposed,
#                 'equivocation_score': 0-100 (higher = more equivocal),
#                 'flagged_components': {component_index: [categories]}
#             }
#         """
#         # is_decomposed = statement.startswith('[DECOMPOSED]')
        
#         # if is_decomposed:
#         #     # Extract components from tree structure
#         #     components = []
#         #     for line in statement.split('\n')[1:]:
#         #         # Remove tree characters
#         #         clean = re.sub(r'[├─└│\s]+', '', line).strip()
#         #         if clean:
#         #             components.append(clean)
#         # else:
#         #     components = [statement]
        
#         # flagged = {}
#         # equivocation_count = 0
#         # total_words = sum(len(c.split()) for c in components)
        
#         # for i, component in enumerate(components):
#         #     component_lower = component.lower()
#         #     component_flags = []
            
#         #     for category, markers in EquivocationDetector.EQUIVOCAL_MARKERS.items():
#         #         for marker in markers:
#         #             if marker in component_lower:
#         #                 component_flags.append(category)
#         #                 equivocation_count += 1
#         #                 break  # Count each category once per component
            
#         #     if component_flags:
#         #         flagged[i] = list(set(component_flags))
        
#         # # Calculate equivocation score (0-100)
#         # equivocation_score = min(100, int((equivocation_count / max(1, total_words // 5)) * 100))
        
#         # return {
#         #     'is_decomposed': is_decomposed,
#         #     'components': components,
#         #     'equivocation_score': equivocation_score,
#         #     'flagged_components': flagged,
#         #     'has_deflection': any('deflection' in flags for flags in flagged.values()),
#         #     'has_contradiction': any('contradiction' in flags for flags in flagged.values()),
#         #     'has_hedging': any('hedging' in flags for flags in flagged.values()),
#         # }

#         # Run standard decomposition first if it hasn't been formatted yet
#         if not statement.startswith('[DECOMPOSED]'):
#             EchologyAmongUsAdaptor.decompose_statement(statement)
            
#         units: List[DecomposedUnit] = getattr(EchologyAmongUsAdaptor, '_last_analysis', [])
        
#         if not units:
#             return {'equivocation_score': 0, 'has_deflection': False, 'has_contradiction': False, 'has_hedging': False}

#         # Pull aggregations directly from the units
#         max_attention = max(u.attention_score for u in units)
#         highest_risk = "LOW"
#         if any(u.risk_category == "high_deception_risk" for u in units):
#             highest_risk = "HIGH"
#         elif any(u.risk_category == "medium_risk" for u in units):
#             highest_risk = "MEDIUM"

#         # Map dynamic attributes back to agent.py requirements
#         has_deflection = any(any(m in u.text.lower() for m in ['anyway', 'moving on']) for u in units)
#         has_contradiction = any(any(m in u.text.lower() for m in ['but', 'however']) for u in units)
#         has_hedging = any(any(m in u.text.lower() for m in ['i think', 'maybe']) for u in units)

#         return {
#             'is_decomposed': True,
#             'components': [u.text for u in units],
#             'equivocation_score': int(max_attention * 10), # Normalized to 0-100 scale
#             'flagged_components': {i: [u.risk_category] for i, u in enumerate(units) if u.risk_category != "low_risk"},
#             'has_deflection': has_deflection,
#             'has_contradiction': has_contradiction,
#             'has_hedging': has_hedging,
#             'risk_assessment': highest_risk
#         }
    
#     @staticmethod
#     def get_risk_assessment(analysis_result):
#         """
#         Returns a human-readable risk assessment based on analysis.
        
#         Args:
#             analysis_result: Output from analyze_statement()
            
#         Returns:
#             str: Risk assessment (LOW, MEDIUM, HIGH)
#         """
#         return analysis_result.get('risk_assessment', 'LOW')
#         # score = analysis_result['equivocation_score']
#         # has_deflection = analysis_result['has_deflection']
#         # has_contradiction = analysis_result['has_contradiction']
#         # has_hedging = analysis_result['has_hedging'
        
#         # # Assess based on patterns
#         # risk_factors = 0
#         # if score > 50:
#         #     risk_factors += 2
#         # if score > 70:
#         #     risk_factors += 2
#         # if has_deflection:
#         #     risk_factors += 1
#         # if has_contradiction:
#         #     risk_factors += 1
#         # if has_hedging and has_deflection:
#         #     risk_factors += 1  # Combination is more suspicious
        
#         # if risk_factors >= 4:
#         #     return "HIGH"
#         # elif risk_factors >= 2:
#         #     return "MEDIUM"
#         # else:
#         #     return "LOW"