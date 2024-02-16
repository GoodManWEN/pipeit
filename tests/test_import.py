import os, sys
sys.path.append(os.getcwd())
import pytest
from pipeit import *

@pytest.mark.asyncio
async def test_import():
    ...