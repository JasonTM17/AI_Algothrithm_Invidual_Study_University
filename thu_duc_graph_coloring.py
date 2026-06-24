"""Thu Duc city graph-coloring CSP demo data and solver helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


Region = str
Edge = Tuple[Region, Region]

REGIONS: Tuple[Region, ...] = (
    "Linh Xuan",
    "Binh Chieu",
    "Linh Trung",
    "Tam Binh",
    "Tam Phu",
    "Hiep Binh Phuoc",
    "Hiep Binh Chanh",
    "Linh Dong",
    "Linh Tay",
    "Linh Chieu",
    "Truong Tho",
    "Binh Tho",
    "An Binh",
    "Phuoc Long A",
    "Phuoc Long B",
    "Tang Nhon Phu B",
    "Tang Nhon Phu A",
    "Hiep Phu",
    "Phuoc Binh",
    "Phu Huu",
    "Long Truong",
    "Truong Thanh",
    "Long Phuoc",
    "Long Binh",
)

EDGES: Tuple[Edge, ...] = (
    ("Linh Xuan", "Binh Chieu"),
    ("Linh Xuan", "Linh Trung"),
    ("Binh Chieu", "Tam Binh"),
    ("Binh Chieu", "Hiep Binh Phuoc"),
    ("Tam Binh", "Tam Phu"),
    ("Tam Binh", "Linh Dong"),
    ("Tam Phu", "Hiep Binh Chanh"),
    ("Tam Phu", "Linh Dong"),
    ("Hiep Binh Phuoc", "Hiep Binh Chanh"),
    ("Hiep Binh Chanh", "Linh Dong"),
    ("Linh Dong", "Linh Tay"),
    ("Linh Tay", "Linh Trung"),
    ("Linh Tay", "Linh Chieu"),
    ("Linh Chieu", "Linh Trung"),
    ("Linh Chieu", "Binh Tho"),
    ("Linh Chieu", "Truong Tho"),
    ("Truong Tho", "Binh Tho"),
    ("Truong Tho", "An Binh"),
    ("Binh Tho", "An Binh"),
    ("Binh Tho", "Hiep Phu"),
    ("An Binh", "Phuoc Long A"),
    ("Phuoc Long A", "Phuoc Long B"),
    ("Phuoc Long A", "Hiep Phu"),
    ("Phuoc Long B", "Tang Nhon Phu B"),
    ("Phuoc Long B", "Phuoc Binh"),
    ("Hiep Phu", "Tang Nhon Phu B"),
    ("Hiep Phu", "Tang Nhon Phu A"),
    ("Tang Nhon Phu B", "Tang Nhon Phu A"),
    ("Tang Nhon Phu B", "Phuoc Binh"),
    ("Tang Nhon Phu A", "Truong Thanh"),
    ("Tang Nhon Phu A", "Long Binh"),
    ("Phuoc Binh", "Phu Huu"),
    ("Phuoc Binh", "Truong Thanh"),
    ("Phu Huu", "Long Truong"),
    ("Phu Huu", "Truong Thanh"),
    ("Long Truong", "Truong Thanh"),
    ("Long Truong", "Long Phuoc"),
    ("Truong Thanh", "Long Phuoc"),
    ("Truong Thanh", "Long Binh"),
    ("Long Phuoc", "Long Binh"),
    ("Long Binh", "Linh Trung"),
    ("Linh Trung", "Binh Tho"),
)

PALETTE: Tuple[str, ...] = (
    "Xanh ngoc",
    "Vang dat",
    "Do gach",
    "Tim than",
    "Xanh troi",
    "Hong sen",
)

WARD_POSITIONS: Dict[Region, Tuple[float, float]] = {
    "Linh Xuan": (0.16, 0.08),
    "Binh Chieu": (0.18, 0.24),
    "Linh Trung": (0.38, 0.14),
    "Tam Binh": (0.28, 0.34),
    "Tam Phu": (0.38, 0.36),
    "Hiep Binh Phuoc": (0.12, 0.43),
    "Hiep Binh Chanh": (0.26, 0.51),
    "Linh Dong": (0.43, 0.48),
    "Linh Tay": (0.50, 0.30),
    "Linh Chieu": (0.56, 0.40),
    "Truong Tho": (0.46, 0.62),
    "Binh Tho": (0.62, 0.56),
    "An Binh": (0.54, 0.73),
    "Phuoc Long A": (0.70, 0.72),
    "Phuoc Long B": (0.79, 0.63),
    "Tang Nhon Phu B": (0.88, 0.51),
    "Tang Nhon Phu A": (0.78, 0.38),
    "Hiep Phu": (0.69, 0.48),
    "Phuoc Binh": (0.88, 0.72),
    "Phu Huu": (0.78, 0.86),
    "Long Truong": (0.64, 0.91),
    "Truong Thanh": (0.69, 0.72),
    "Long Phuoc": (0.50, 0.91),
    "Long Binh": (0.58, 0.24),
}


@dataclass(frozen=True)
class ColoringResult:
    assignments: Dict[Region, str]
    colors_used: Tuple[str, ...]
    conflicts: List[Edge]
    steps: List[Dict[str, str]]

    @property
    def valid(self) -> bool:
        return not self.conflicts


def regions() -> Tuple[Region, ...]:
    return REGIONS


def validate_coloring(assignments: Dict[Region, str]) -> List[Edge]:
    return [
        (left, right)
        for left, right in EDGES
        if assignments.get(left) and assignments.get(left) == assignments.get(right)
    ]


def _neighbors(region: Region) -> List[Region]:
    return [right if left == region else left for left, right in EDGES if left == region or right == region]


def color_graph(max_colors: int = 4) -> ColoringResult:
    palette = PALETTE[: max(1, min(max_colors, len(PALETTE)))]
    assignments: Dict[Region, str] = {}
    steps: List[Dict[str, str]] = []
    adjacency = {region: _neighbors(region) for region in REGIONS}

    def choose_unassigned_region() -> Region:
        candidates = [region for region in REGIONS if region not in assignments]
        return min(
            candidates,
            key=lambda region: (
                -len({assignments[neighbor] for neighbor in adjacency[region] if neighbor in assignments}),
                -len(adjacency[region]),
                region,
            ),
        )

    def assign_next_region() -> bool:
        if len(assignments) == len(REGIONS):
            return True

        region = choose_unassigned_region()
        blocked = {assignments[neighbor] for neighbor in adjacency[region] if neighbor in assignments}
        for chosen in palette:
            if chosen in blocked:
                continue
            assignments[region] = chosen
            steps.append(
                {
                    "Region": region,
                    "Blocked colors": ", ".join(sorted(blocked)) or "-",
                    "Chosen color": chosen,
                    "Degree": str(len(adjacency[region])),
                }
            )
            if assign_next_region():
                return True
            steps.pop()
            del assignments[region]
        return False

    if not assign_next_region():
        # Keep the UI inspectable for impossible palettes by returning a complete
        # greedy coloring with conflicts instead of partial assignments.
        assignments.clear()
        steps.clear()
        ordered_regions = sorted(REGIONS, key=lambda region: (-len(adjacency[region]), region))
        for region in ordered_regions:
            blocked = {assignments[neighbor] for neighbor in adjacency[region] if neighbor in assignments}
            chosen = next((color for color in palette if color not in blocked), palette[0])
            assignments[region] = chosen
            steps.append(
                {
                    "Region": region,
                    "Blocked colors": ", ".join(sorted(blocked)) or "-",
                    "Chosen color": chosen,
                    "Degree": str(len(adjacency[region])),
                }
            )

    used_colors = set(assignments.values())
    used = tuple(color for color in palette if color in used_colors)
    return ColoringResult(assignments, used, validate_coloring(assignments), steps)


def coloring_rows(result: ColoringResult) -> List[Dict[str, str]]:
    return [
        {
            "Region": region,
            "Color": result.assignments[region],
            "Adjacent count": str(len(_neighbors(region))),
            "Adjacent regions": ", ".join(_neighbors(region)),
        }
        for region in REGIONS
    ]
