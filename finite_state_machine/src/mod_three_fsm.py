
"""
Authors : Kyaw Kyaw Oo
Emails : kyaw.tech@gmail.com
Started Date : May 18, 2025
Description : Implementation of a finite state machine (FSM) to compute the modulo-3 of binary input streams. Designed to simulate digital logic behavior for pattern recognition.
Released Date : May 18, 2025
CopyRight@2025 by Kyaw Kyaw Oo
"""

import logging
from enum import Enum, auto
from typing import Dict, Set, Callable, Any, TypeVar

# Set up logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fsm.log')
    ]
)

logger = logging.getLogger('FSM')
T = TypeVar('T')

class State(Enum):
    """Base class for FSM states."""
    pass

class FSM:
    """
    A generic Finite State Machine implementation with logging.
    """
    
    def __init__(self, states: Set[State], alphabet: Set[str], initial_state: State, 
                 final_states: Set[State], transition_function: Dict[State, Dict[str, State]]):
        logger.info("Initializing FSM")
        logger.debug(f"States: {states}")
        logger.debug(f"Alphabet: {alphabet}")
        logger.debug(f"Initial state: {initial_state}")
        logger.debug(f"Final states: {final_states}")
        
        self.states = states
        self.alphabet = alphabet
        self.initial_state = initial_state
        self.final_states = final_states
        self.transition_function = transition_function
        self.current_state = initial_state
        
        self._validate_fsm()
        logger.info("FSM initialized successfully")
    
    def _validate_fsm(self) -> None:
        """Validate the FSM configuration."""
        logger.debug("Validating FSM configuration")
        
        if self.initial_state not in self.states:
            error_msg = "Initial state must be in the set of states"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not self.final_states.issubset(self.states):
            error_msg = "Final states must be a subset of states"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        for state in self.transition_function:
            if state not in self.states:
                error_msg = f"Transition state {state} not in states set"
                logger.error(error_msg)
                raise ValueError(error_msg)
            for symbol, next_state in self.transition_function[state].items():
                if symbol not in self.alphabet:
                    error_msg = f"Symbol {symbol} not in alphabet"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                if next_state not in self.states:
                    error_msg = f"Next state {next_state} not in states set"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
        
        logger.debug("FSM validation successful")
    
    def reset(self) -> None:
        """Reset the FSM to its initial state."""
        logger.debug(f"Resetting FSM from {self.current_state} to {self.initial_state}")
        self.current_state = self.initial_state
    
    def process_input(self, input_symbol: str) -> State:
        """
        Process a single input symbol and transition to the next state.
        """
        logger.debug(f"Processing input '{input_symbol}' from state {self.current_state}")
        
        if input_symbol not in self.alphabet:
            error_msg = f"Input symbol '{input_symbol}' not in alphabet"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        previous_state = self.current_state
        self.current_state = self.transition_function[self.current_state][input_symbol]
        logger.debug(f"Transitioned from {previous_state} to {self.current_state} on input '{input_symbol}'")
        return self.current_state
    
    def process_string(self, input_string: str) -> State:
        """
        Process an entire string of input symbols.
        """
        logger.info(f"Processing input string: '{input_string}'")
        
        if not input_string:
            error_msg = "Input string cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        for symbol in input_string:
            self.process_input(symbol)
        
        logger.info(f"Finished processing. Final state: {self.current_state}")
        return self.current_state
    
    def is_in_final_state(self) -> bool:
        """Check if the current state is a final/accepting state."""
        result = self.current_state in self.final_states
        logger.debug(f"Checking final state: {self.current_state} in {self.final_states} -> {result}")
        return result


class ModThreeState(State):
    """States for the Modulo Three FSM."""
    S0 = auto()
    S1 = auto()
    S2 = auto()


class ModThreeFSM(FSM):
    """
    Finite State Machine that calculates modulo 3 of a binary number with logging.
    """
    
    def __init__(self):
        logger.info("Initializing ModThreeFSM")
        states = {ModThreeState.S0, ModThreeState.S1, ModThreeState.S2}
        alphabet = {'0', '1'}
        initial_state = ModThreeState.S0
        final_states = {ModThreeState.S0, ModThreeState.S1, ModThreeState.S2}
        
        transition_function = {
            ModThreeState.S0: {
                '0': ModThreeState.S0,
                '1': ModThreeState.S1
            },
            ModThreeState.S1: {
                '0': ModThreeState.S2,
                '1': ModThreeState.S0
            },
            ModThreeState.S2: {
                '0': ModThreeState.S1,
                '1': ModThreeState.S2
            }
        }
        
        super().__init__(states, alphabet, initial_state, final_states, transition_function)
        logger.info("ModThreeFSM initialized successfully")
    
    def calculate_remainder(self, binary_string: str) -> int:
        """
        Calculate the remainder when the binary number is divided by 3.
        """
        logger.info(f"Calculating remainder for binary string: '{binary_string}'")
        
        if not binary_string:
            error_msg = "Input string cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not all(c in self.alphabet for c in binary_string):
            error_msg = "Input string must contain only '0's and '1's"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        final_state = self.process_string(binary_string)
        self.reset()
        
        remainder_map = {
            ModThreeState.S0: 0,
            ModThreeState.S1: 1,
            ModThreeState.S2: 2
        }
        
        if final_state not in remainder_map:
            error_msg = f"Invalid final state: {final_state}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        remainder = remainder_map[final_state]
        logger.info(f"Calculation complete. Remainder: {remainder}")
        return remainder