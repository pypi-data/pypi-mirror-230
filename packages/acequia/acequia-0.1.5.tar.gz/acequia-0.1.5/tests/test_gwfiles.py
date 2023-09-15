
import pytest
import collections
import numpy as np
from pandas import DataFrame
import pandas as pd
from acequia import GwFiles, GwSeries
import acequia as aq

dinodir = '.\\data\\dinogws\\'
jsondir = '.\\output\\json\\'
csvdir = '.\\output\\csv\\'

@pytest.fixture
def gwf():
    return GwFiles.from_dinocsv(dinodir)

@pytest.fixture
def gwf_json():
    return GwFiles.from_json(jsondir)

def test_from_dinocsv_with_only_filedir():
    gwf = GwFiles.from_dinocsv(dinodir)
    assert isinstance(gwf.filetable,DataFrame)
    assert not gwf.filetable.empty

def test_from_dinocsv_with_loclist(gwf):
    loclist = gwf.filetable['loc'].values

    gwf2 = GwFiles.from_dinocsv(dinodir,loclist=loclist)
    assert isinstance(gwf2.filetable,DataFrame)
    assert len(gwf2.filetable)!=0

def test_from_json_with_only_filedir():

    gwf = GwFiles.from_json(jsondir)
    assert isinstance(gwf.filetable,DataFrame)
    assert not gwf.filetable.empty

def test_from_json_with_loclist(gwf):

    loclist = gwf.filetable['loc'].values ##[:listlen]

    gwf2 = GwFiles.from_json(jsondir,loclist=loclist)
    assert isinstance(gwf2.filetable,DataFrame)
    assert len(gwf2.filetable)!=0

def test_init_with_invalid_input():

    with pytest.raises(ValueError):
        gwf = GwFiles('A_String')

    with pytest.raises(ValueError):
        badcolumns = DataFrame(columns=['A','B','C',])
        gwf = GwFiles(badcolumns)

def test_repr(gwf):

    assert isinstance(repr(gwf),str)

def test_iteritems(gwf, gwf_json):

    for gw in gwf.iteritems():
        assert isinstance(gw,GwSeries)

    for gw in gwf_json.iteritems():
        assert isinstance(gw,GwSeries)


def test_to_json(gwf):

    jsn = gwf.to_json(jsondir)
    assert isinstance(jsn,list)
    assert isinstance(jsn[0],collections.OrderedDict)

def test_to_csv(gwf):

    csv = gwf.to_csv(csvdir)
    assert isinstance(csv,list)
    assert isinstance(csv[0],pd.Series)

