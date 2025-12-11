class SymbolTable:
    """Associates symbolic labels to numeric addresses"""

    def __init__(self) -> None:
        """Initializes symbol table with predefined symbols"""
        self._dict = {
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "SCREEN": 16384,
            "KBD": 24576,
        }

    def add_entry(self, symbol: str, address: int) -> None:
        """Add the pair (symbol, address) to the symbol table"""
        self._dict[symbol] = address

    def contains(self, symbol: str) -> bool:
        """Check if the symbol table contains the given symbol"""
        return symbol in self._dict

    def get_address(self, symbol: str) -> int:
        """Get the address that a symbol corresponds to"""
        return self._dict[symbol]
