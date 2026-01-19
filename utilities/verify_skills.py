#!/usr/bin/env python3
"""
Verify Rhea Skills
Iterates through all registered skills, tests routing with triggers,
and verifies the skill module can be loaded.
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rhea_noir.router.config import SKILL_CATALOG
from rhea_noir.router import reflex
from rhea_noir.skills import registry
from rich.console import Console
from rich.table import Table

console = Console()

def verify_all():
    console.print("[bold]🔍 Verifying Rhea Skills...[/bold]")
    
    results = []
    print(f"{'SKILL':<15} | {'TRIGGER':<20} | {'ROUTING':<10} | {'LOADING':<10} | STATUS")
    print("-" * 80)

    for skill_name, info in SKILL_CATALOG.items():
        # 1. Test Routing
        triggers = info.get("triggers", [])
        if not triggers:
            print(f"{skill_name:<15} | {'N/A':<20} | NO_TRIG    | -          | ⚠️")
            continue
            
        test_trigger = triggers[0]
        
        # Route
        try:
            route_res = reflex.route(test_trigger)
            routed_skill = route_res.get("skill")
            
            if routed_skill == skill_name:
                routing_status = "PASS"
            else:
                routing_status = f"FAIL({routed_skill})"
                
        except Exception as e:
            routing_status = "ERROR"
            routed_skill = None

        # 2. Test Loading (Registry)
        try:
            skill_obj = registry.get(skill_name)
            if skill_obj:
                loading_status = "PASS"
            else:
                # Debug: Try explicit import to see error
                try:
                    import importlib
                    importlib.import_module(f"rhea_noir.skills.{skill_name}.actions")
                    loading_status = "FAIL(Reg/NoSkillObj)"
                except Exception as e:
                    loading_status = f"ERR:{type(e).__name__}"
                    # Print full error to console for debug
                    print(f"\n[DEBUG] Failed to import {skill_name}: {e}")
        except Exception as e:
            loading_status = "ERROR"
            
        # Overall Pass?
        if routing_status == "PASS" and loading_status == "PASS":
            emoji = "✅"
        else:
            emoji = "❌"
            
        print(f"{skill_name:<15} | {test_trigger[:20]:<20} | {routing_status:<10} | {loading_status:<10} | {emoji}")

if __name__ == "__main__":
    verify_all()
