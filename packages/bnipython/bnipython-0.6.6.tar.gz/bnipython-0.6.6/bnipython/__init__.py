from bnipython.lib.bniClient import BNIClient
from bnipython.lib.api.oneGatePayment import OneGatePayment
from bnipython.lib.api.snapBI import SnapBI
import sys
sys.modules['BNIClient'] = BNIClient
sys.modules['OneGatePayment'] = OneGatePayment
sys.modules['SnapBI'] = SnapBI
