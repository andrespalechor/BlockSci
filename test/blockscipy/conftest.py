import pytest
import subprocess
import os


def pytest_addoption(parser):
    parser.addoption("--btc", action="store_true",
                     help="Run tests for Bitcoin")
    parser.addoption("--bch", action="store_true",
                     help="Run tests for Bitcoin Cash")


def pytest_generate_tests(metafunc):
    metafunc.fixturenames.append('chain_name')
    chains = []
    if metafunc.config.option.btc:
        chains += ["btc"]
    if metafunc.config.option.bch:
        chains += ["bch"]
    if not chains:
        chains = ["btc", "bch"]
    metafunc.parametrize('chain_name', chains, scope="session")


def pytest_runtest_call(item):
    markers = [x.name for x in item.iter_markers()]
    if markers:
        if item.funcargs['chain_name'] not in markers:
            pytest.skip("Skipping test for chain {}".format(item.funcargs['chain_name']))


@pytest.fixture(scope="session")
def chain(tmpdir_factory, chain_name):
    temp_dir = tmpdir_factory.mktemp(chain_name)
    chain_dir = str(temp_dir)

    if chain_name == "btc":
        blocksci_chain_name = "bitcoin_regtest"
    elif chain_name == "bch":
        blocksci_chain_name = "bitcoin_cash_regtest"
    else:
        raise ValueError("Invalid chain name {}".format(chain_name))

    create_config_cmd = ["blocksci_parser", chain_dir + "/config.json", "generate-config", blocksci_chain_name,
                         chain_dir, "--disk", "../files/{}/regtest/".format(chain_name)]
    subprocess.run(create_config_cmd, check=True)

    parse_cmd = ["blocksci_parser", chain_dir + "/config.json", "update"]
    subprocess.run(parse_cmd, check=True)

    import blocksci
    chain = blocksci.Blockchain(chain_dir + "/config.json")
    return chain


@pytest.fixture
def json_data(chain_name):
    import json
    with open("../files/{}/output.json".format(chain_name), "r") as f:
        return json.load(f)