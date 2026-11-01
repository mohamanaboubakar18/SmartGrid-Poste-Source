"""
Module d'interfaçage Automate (PLC) - Simulateur Smart Grid
Compatible Beckhoff TwinCAT (protocole ADS via pyads) & Modbus TCP.
Permet d'envoyer les consignes de simulation (délestage, état disjoncteur,
température point chaud) vers un automate industriel ou une IHM de supervision.
"""

import time
import logging

# Configuration du logger industriel
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [PLC-INTERFACE] %(message)s')

try:
    import pyads
    PYADS_AVAILABLE = True
except ImportError:
    PYADS_AVAILABLE = False


class BeckhoffSimulationInterface:
    """
    Gestionnaire d'interface entre le simulateur Python et un automate Beckhoff (TwinCAT 3).
    Inclut un mode 'Mock/Simulation' automatique lorsqu'aucun automate physique n'est connecté.
    """
    def __init__(self, ams_net_id: str = "127.0.0.1.1.1", port: int = 851, simulation_mode: bool = True):
        self.ams_net_id = ams_net_id
        self.port = port
        self.simulation_mode = simulation_mode or not PYADS_AVAILABLE
        self.plc = None
        self.connected = False
        self.virtual_plc_memory = {
            "GVL.bLoadSheddingOrder": False,
            "GVL.rTransformerTempC": 65.0,
            "GVL.rGridLoadPercent": 72.5,
            "GVL.bBreakerStatus": True
        }

    def connect(self) -> bool:
        """Établit la liaison ADS avec le runtime TwinCAT ou active le bus virtuel."""
        if not self.simulation_mode:
            try:
                self.plc = pyads.Connection(self.ams_net_id, self.port)
                self.plc.open()
                self.connected = True
                logging.info(f"Connecté à l'automate Beckhoff ({self.ams_net_id}:{self.port}) via ADS.")
            except Exception as e:
                logging.warning(f"Automate physique non détecté ({e}). Basculement en mode Simulation IHM.")
                self.simulation_mode = True
                self.connected = True
        else:
            self.connected = True
            logging.info(f"Interface de simulation initialisée (Cible : TwinCAT ADS {self.ams_net_id}:{self.port}).")
        return self.connected

    def write_variable(self, symbol_name: str, value) -> None:
        """Écrit une consigne de simulation vers une variable automate (GVL)."""
        if not self.connected:
            raise ConnectionError("L'interface automate n'est pas connectée.")
        
        if not self.simulation_mode and self.plc:
            self.plc.write_by_name(symbol_name, value)
        else:
            self.virtual_plc_memory[symbol_name] = value
            logging.info(f"Écriture ADS -> {symbol_name} = {value}")

    def read_variable(self, symbol_name: str):
        """Lit l'état d'une variable automate pour mise à jour de l'IHM."""
        if not self.simulation_mode and self.plc:
            return self.plc.read_by_name(symbol_name)
        return self.virtual_plc_memory.get(symbol_name, None)

    def sync_smartgrid_step(self, load_pct: float, temp_c: float, shedding_active: bool) -> dict:
        """Synchronise un pas de calcul du simulateur réseau avec les registres de l'automate."""
        self.write_variable("GVL.rGridLoadPercent", round(load_pct, 2))
        self.write_variable("GVL.rTransformerTempC", round(temp_c, 2))
        self.write_variable("GVL.bLoadSheddingOrder", bool(shedding_active))
        
        # Logique sécurité : ouverture disjoncteur si surcharge critique (> 115 %)
        breaker_closed = load_pct <= 115.0
        self.write_variable("GVL.bBreakerStatus", breaker_closed)
        
        return self.virtual_plc_memory

    def close(self) -> None:
        if not self.simulation_mode and self.plc:
            self.plc.close()
        self.connected = False
        logging.info("Connexion interface automate fermée proprement.")


if __name__ == "__main__":
    # Test unitaire de l'interface de simulation d'automatisme
    plc_interface = BeckhoffSimulationInterface(ams_net_id="192.168.1.50.1.1", port=851, simulation_mode=True)
    plc_interface.connect()

    # Scénario de test : montée de charge sur un poste HT/BT et déclenchement délestage
    test_scenarios = [
        {"load": 78.0, "temp": 68.5, "shedding": False},
        {"load": 96.4, "temp": 84.2, "shedding": True},
        {"load": 118.0, "temp": 98.0, "shedding": True},  # Déclenchement sécurité disjoncteur
    ]

    for step, data in enumerate(test_scenarios, 1):
        print(f"\n--- Cycle de simulation #{step} ---")
        state = plc_interface.sync_smartgrid_step(
            load_pct=data["load"],
            temp_c=data["temp"],
            shedding_active=data["shedding"]
        )
        time.sleep(0.3)

    plc_interface.close()