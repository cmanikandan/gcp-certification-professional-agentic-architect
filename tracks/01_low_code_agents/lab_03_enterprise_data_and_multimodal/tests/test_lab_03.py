import pytest
import sys
import pathlib
import asyncio

lab_dir = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(lab_dir))

import lab

def test_acl_search_filtering():
    """Verify that identity propagation simulator enforces ACLs."""
    datastore = lab.MockDatastore()
    
    # Alice should see 2 docs: Public (*) and Project X (engineering)
    alice_results = datastore.search("policy", "alice@example.com", ["engineering"])
    assert len(alice_results) == 2
    
    # Charlie should see 1 doc: Public (*)
    charlie_results = datastore.search("policy", "charlie@example.com", [])
    assert len(charlie_results) == 1

def test_offline_run_does_not_crash(capsys):
    """The offline run must complete successfully without network calls."""
    asyncio.run(lab.run_offline())
    captured = capsys.readouterr()
    assert "All 3 checks passed" in captured.out
