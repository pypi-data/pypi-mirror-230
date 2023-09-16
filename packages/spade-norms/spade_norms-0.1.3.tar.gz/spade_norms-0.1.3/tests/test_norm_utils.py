from spade_norms.norms.norm import Norm
from spade_norms.norms.norm_enums import *
from spade_norms.norms.norm_utils import * 
import pytest

class TestNormUtils:

    def test_add_single_empty_db(self):
        db = {}
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True)
        assert len(db.values()) == 0
        
        add_single(db, norm)
        assert len(db.values()) == 1

    def test_add_single_same_domain(self):
        db = {}
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True)
        add_single(db, norm)
        assert len(db[0]) == 1

        norm2 =  Norm('test2', NormType.PROHIBITION, lambda x : True)
        add_single(db, norm2)
        assert len(db[0]) == 2

    def test_add_single_repeated_norm(self):
        db = {}
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True)
        add_single(db, norm)
        assert len(db[0]) == 1
        with pytest.raises(Exception):
            add_single(db, norm)

    def test_add_single_different_domain(self):
        db = {}
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True)
        add_single(db, norm)
        assert len(db[0]) == 1

        norm2 =  Norm('test2', NormType.PROHIBITION, lambda x : True, domain=1)
        add_single(db, norm2)
        assert len(db[0]) == 1
        assert len(db[1]) == 1

    def test_add_multiple_empty_db(self):
        db = {}
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True)
        norm2 =  Norm('test2', NormType.PROHIBITION, lambda x : True)
        norm_list = [norm, norm2]

        add_multiple(db, norm_list)
        assert len(db[0]) == 2

    def test_add_multiple_empty_db_different_domain(self):
        db = {}
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True)
        norm2 =  Norm('test2', NormType.PROHIBITION, lambda x : True, domain=1)
        norm_list = [norm, norm2]

        add_multiple(db, norm_list)
        assert len(db[0]) == 1
        assert len(db[1]) == 1

    def test_add_multiple_same_domain(self):
        db = {0: [Norm('test', NormType.PROHIBITION, lambda x : True)], 1: [Norm('test2', NormType.PROHIBITION, lambda x : True, domain=1)]}
        norm =  Norm('test3', NormType.PROHIBITION, lambda x : True)
        norm2 =  Norm('test4', NormType.PROHIBITION, lambda x : True)
        norm_list = [norm, norm2]

        add_multiple(db, norm_list)
        assert len(db[0]) == 3
        assert len(db[1]) == 1

    def test_add_multiple_different_domain(self):
        db = {0: [Norm('test', NormType.PROHIBITION, lambda x : True)], 1: [Norm('test2', NormType.PROHIBITION, lambda x : True, domain=1)]}
        norm =  Norm('test3', NormType.PROHIBITION, lambda x : True)
        norm2 =  Norm('test4', NormType.PROHIBITION, lambda x : True, domain = 1)
        norm_list = [norm, norm2]

        add_multiple(db, norm_list)
        assert len(db[0]) == 2
        assert len(db[1]) == 2

    def test_add_multiple_empty_list_empty_db(self):
        db = {}
        norm_list = []

        add_multiple(db, norm_list)
        assert len(db.values()) == 0

    def test_add_multiple_empty_list(self):
        db = {0: [Norm('test', NormType.PROHIBITION, lambda x : True)], 1: [Norm('test2', NormType.PROHIBITION, lambda x : True, domain=1)]}
        norm_list = []
        add_multiple(db, norm_list)
        assert len(db[0]) == 1
        assert len(db[1]) == 1

    def test_contains_norm_True(self):
        db = {0: [Norm('test', NormType.PROHIBITION, lambda x : True)]}
        norm = Norm('test', NormType.PROHIBITION, lambda x : True)
        assert contains(db, norm) == True

    def test_contains_norm_False(self):
        db = {0: [Norm('test', NormType.PROHIBITION, lambda x : True)]}
        norm = Norm('test2', NormType.PROHIBITION, lambda x : True)
        assert contains(db, norm) == False

    def test_contains_norm_False_empty_db(self):
        db = {}
        norm = Norm('test2', NormType.PROHIBITION, lambda x : True)
        assert contains(db, norm) == False

    def test_remove_norm(self):
        db = {0: [Norm('test', NormType.PROHIBITION, lambda x : True)]}
        norm = Norm('test', NormType.PROHIBITION, lambda x : True)
        db = remove(db, norm)
        assert len(db.values()) == 0

    def test_remove_norm_not_in_db(self):
        db = {0: [Norm('test', NormType.PROHIBITION, lambda x : True)]}
        norm = Norm('test1', NormType.PROHIBITION, lambda x : True)
        db = remove(db, norm)
        assert len(db.values()) == 1

    def test_remove_norm_empty_db(self):
        db = {}
        norm = Norm('test', NormType.PROHIBITION, lambda x : True)
        db = remove(db, norm)
        assert len(db.values()) == 0

    def test_filter_norms_by_role_existing(self):
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True, roles=[1])
        norm2 =  Norm('test2', NormType.PROHIBITION, lambda x : True, roles=[1])
        norm_list = [norm, norm2]
        role = 1
        assert len(filter_norms_by_role(norm_list, role)) == 2

    def test_filter_norms_by_role_empty_normlist(self):
        norm_list = []
        role = 1
        assert len(filter_norms_by_role(norm_list, role)) == 0

    def test_filter_norms_by_role_non_existing(self):
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True, roles=[1])
        norm2 =  Norm('test2', NormType.PROHIBITION, lambda x : True, roles=[1])
        norm_list = [norm, norm2]
        role = 2
        assert len(filter_norms_by_role(norm_list, role)) == 0

    def test_filter_norms_by_role_non_existing(self):
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True, roles=[])
        norm2 =  Norm('test2', NormType.PROHIBITION, lambda x : True, roles=[])
        norm_list = [norm, norm2]
        role = None
        assert len(filter_norms_by_role(norm_list, role)) == 2

    def test_filter_norms_by_role_none(self):
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True, roles=[])
        norm2 =  Norm('test2', NormType.PROHIBITION, lambda x : True, roles=[])
        norm_list = [norm, norm2]
        role = 1
        assert len(filter_norms_by_role(norm_list, role)) == 2

    def test_filter_norms_by_role_multiple(self):
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True, roles=[1,2,3])
        norm2 =  Norm('test2', NormType.PROHIBITION, lambda x : True, roles=[1,3])
        norm_list = [norm, norm2]
        role = 2
        assert len(filter_norms_by_role(norm_list, role)) == 1

    def test_join_norms_and_concerns(self):
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True, roles=[1,2,3])
        concern =  Norm('test2', NormType.PROHIBITION, lambda x : True, roles=[1,3])
        norm_list = [norm]
        concern_list = [concern]
        assert len(join_norms_and_concerns(norm_list, concern_list)) == 2

    def test_join_norms_and_concerns_empty_norms(self):
        concern =  Norm('test2', NormType.PROHIBITION, lambda x : True, roles=[1,3])
        norm_list = []
        concern_list = [concern]
        assert len(join_norms_and_concerns(norm_list, concern_list)) == 1

    def test_join_norms_and_concerns_empty_concerns(self):
        norm =  Norm('test', NormType.PROHIBITION, lambda x : True, roles=[1,2,3])
        norm_list = [norm]
        concern_list = []
        assert len(join_norms_and_concerns(norm_list, concern_list)) == 1

    def test_join_norms_and_concerns_empty_both(self):
        norm_list = []
        concern_list = []
        assert len(join_norms_and_concerns(norm_list, concern_list)) == 0