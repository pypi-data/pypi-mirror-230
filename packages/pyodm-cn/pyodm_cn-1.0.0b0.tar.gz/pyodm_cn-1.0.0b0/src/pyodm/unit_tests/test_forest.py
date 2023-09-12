import pytest

from pyodm.utils.forest import Forest


@pytest.fixture
def data_one():
    return [dict(site_id=1, site_name="D01")]


@pytest.fixture
def tree_array():
    return [
        [dict(id=1), dict(id=2), dict(id=5)],
        [dict(id=1), dict(id=3)],
        [dict(id=1), dict(id=4)]
    ]


def test_transform(tree_array):
    tree = Forest.transform(tree_array)
    assert len(tree.nodes) == 3
    assert tree.degree == 3
    root = tree.root()
    assert root.get("id") == 1

    assert len(root.children()) == 3
    assert root.children()[0].get("id") == 2
    assert root.children()[1].get("id") == 3
    assert root.children()[2].get("id") == 4

    assert root.children()[0].has_child() is True
    assert root.children()[1].has_child() is False
    assert root.children()[2].has_child() is False

    assert root.children()[0].children()[0].get("id") == 5


def test_one_level_tree(data_one):
    tree = Forest.factory(branch=data_one)
    assert len(tree.nodes) == 1
    assert len(tree.get_level_nodes(0)) == 1
    root0 = tree.get_level_nodes(0)[0]
    assert root0.values["site_id"] == 1
    assert root0.values["site_name"] == "D01"
    tree.add_branch(data_one)
    assert len(tree.nodes) == 1
    assert len(tree.get_level_nodes(0)) == 1
    assert root0.values["site_id"] == 1
    assert root0.values["site_name"] == "D01"


@pytest.fixture
def data_two():
    return [[dict(site_id=1, site_name="D01"), dict(subject_id=1, subject_name="S01")],
            [dict(site_id=1, site_name="D01"), dict(subject_id=1, subject_name="S01")],
            [dict(site_id=1, site_name="D01"), dict(subject_id=2, subject_name="S02")],
            [dict(site_id=2, site_name="D02"), dict(subject_id=1, subject_name="S01")],
            [dict(site_id=2, site_name="D02"), dict(subject_id=2, subject_name="S02")],
            [dict(site_id=2, site_name="D02"), dict(subject_id=3, subject_name="S04")],
            [dict(site_id=2, site_name="D03"), dict(subject_id=3, subject_name="S04")]]


def test_two_level_tree(data_two):
    tree = Forest.factory()
    for e in data_two:
        tree.add_branch(e)
        assert len(tree.nodes) == 2

    assert len(tree.get_level_nodes(0)) == 3
    root0 = tree.get_level_nodes(0)[0]
    root1 = tree.get_level_nodes(0)[1]
    root2 = tree.get_level_nodes(0)[2]
    assert root0.values["site_id"] == 1
    assert root0.values["site_name"] == "D01"
    assert root1.values["site_id"] == 2
    assert root1.values["site_name"] == "D02"
    assert root2.values["site_id"] == 2
    assert root2.values["site_name"] == "D03"
    assert len(tree.get_level_nodes(1)) == 6
    assert len(root0.children_index) == 2
    assert root0.find_child(subject_id=1, subject_name="S01") is not None
    assert root0.find_child(subject_id=1, subject_name="S01").parent().satisfy(site_id=1, site_name="D01") is True
    assert root0.find_child(subject_id=2, subject_name="S02") is not None
    assert root0.find_child(subject_id=2, subject_name="S02").parent().satisfy(site_id=1, site_name="D01") is True
    assert len(root1.children_index) == 3
    assert root1.find_child(subject_id=1, subject_name="S01") is not None
    assert root1.find_child(subject_id=1, subject_name="S01").parent().satisfy(site_id=2, site_name="D02") is True
    assert root1.find_child(subject_id=2, subject_name="S02") is not None
    assert root1.find_child(subject_id=2, subject_name="S02").parent().satisfy(site_id=2, site_name="D02") is True
    assert root1.find_child(subject_id=3, subject_name="S04") is not None
    assert root1.find_child(subject_id=3, subject_name="S04").parent().satisfy(site_id=2, site_name="D02") is True
    assert len(root2.children_index) == 1
    assert root2.find_child(subject_id=3, subject_name="S04") is not None
    assert root2.find_child(subject_id=3, subject_name="S04").parent().satisfy(site_id=2, site_name="D03") is True


@pytest.fixture
def data_three():
    return [
        [dict(site_id=1, site_name="D01"), dict(subject_id=1, subject_name="S01"), dict(visit_id=1, visit_name="V01")],
        [dict(site_id=1, site_name="D01"), dict(subject_id=1, subject_name="S01"), dict(visit_id=1, visit_name="V01")],
        [dict(site_id=1, site_name="D01"), dict(subject_id=1, subject_name="S01"), dict(visit_id=2, visit_name="V02")],
        [dict(site_id=1, site_name="D01"), dict(subject_id=2, subject_name="S02"), dict(visit_id=1, visit_name="V01")],
        [dict(site_id=2, site_name="D02"), dict(subject_id=1, subject_name="S01"), dict(visit_id=1, visit_name="V01")],
        [dict(site_id=2, site_name="D02"), dict(subject_id=2, subject_name="S02"), dict(visit_id=2, visit_name="V02")],
        [dict(site_id=2, site_name="D02"), dict(subject_id=3, subject_name="S04"), dict(visit_id=3, visit_name="V03")],
        [dict(site_id=2, site_name="D03"), dict(subject_id=3, subject_name="S04"), dict(visit_id=1, visit_name="V01")]]


def test_three_level_tree(data_three):
    tree = Forest.factory()
    for e in data_three:
        tree.add_branch(e)
    assert len(tree.nodes) == 3
    tree.reset(data_three)
    assert len(tree.nodes) == 3
    assert len(tree.get_level_nodes(0)) == 3
    root0 = tree.get_level_nodes(0)[0]
    root1 = tree.get_level_nodes(0)[1]
    root2 = tree.get_level_nodes(0)[2]
    assert root0.values["site_id"] == 1
    assert root0.values["site_name"] == "D01"
    assert root1.values["site_id"] == 2
    assert root1.values["site_name"] == "D02"
    assert root2.values["site_id"] == 2
    assert root2.values["site_name"] == "D03"
    assert len(tree.get_level_nodes(1)) == 6
    assert len(root0.children_index) == 2
    assert root0.find_child(subject_id=1, subject_name="S01") is not None
    assert root0.find_child(subject_id=1, subject_name="S01").parent().satisfy(site_id=1, site_name="D01") is True
    assert root0.find_child(subject_id=2, subject_name="S02") is not None
    assert root0.find_child(subject_id=2, subject_name="S02").parent().satisfy(site_id=1, site_name="D01") is True
    assert len(root1.children_index) == 3
    assert root1.find_child(subject_id=1, subject_name="S01") is not None
    assert root1.find_child(subject_id=1, subject_name="S01").parent().satisfy(site_id=2, site_name="D02") is True
    assert root1.find_child(subject_id=2, subject_name="S02") is not None
    assert root1.find_child(subject_id=2, subject_name="S02").parent().satisfy(site_id=2, site_name="D02") is True
    assert root1.find_child(subject_id=3, subject_name="S04") is not None
    assert root1.find_child(subject_id=3, subject_name="S04").parent().satisfy(site_id=2, site_name="D02") is True
    assert len(root2.children_index) == 1
    assert root2.find_child(subject_id=3, subject_name="S04") is not None
    assert root2.find_child(subject_id=3, subject_name="S04").parent().satisfy(site_id=2, site_name="D03") is True

    assert len(tree.get_level_nodes(2)) == 7
    assert len(root0.find_child(subject_id=1, subject_name="S01").children_index) == 2
    assert root0.find_child(subject_id=1, subject_name="S01").find_child(visit_id=1,
                                                                         visit_name="V01").parent().parent().satisfy(
        site_id=1, site_name="D01") is True
    assert root0.find_child(subject_id=1, subject_name="S01").find_child(visit_id=2,
                                                                         visit_name="V02").parent().parent().satisfy(
        site_id=1, site_name="D01") is True
    assert len(root0.find_child(subject_id=2, subject_name="S02").children_index) == 1
    assert root0.find_child(subject_id=2, subject_name="S02").find_child(visit_id=1,
                                                                         visit_name="V01").parent().parent().satisfy(
        site_id=1, site_name="D01") is True
    assert len(root1.find_child(subject_id=1, subject_name="S01").children_index) == 1
    assert root1.find_child(subject_id=1, subject_name="S01").find_child(visit_id=1,
                                                                         visit_name="V01").parent().parent().satisfy(
        site_id=2, site_name="D02") is True
    assert len(root1.find_child(subject_id=2, subject_name="S02").children_index) == 1
    assert root1.find_child(subject_id=2, subject_name="S02").find_child(visit_id=2,
                                                                         visit_name="V02").parent().parent().satisfy(
        site_id=2, site_name="D02") is True
    assert len(root1.find_child(subject_id=3, subject_name="S04").children_index) == 1
    assert root1.find_child(subject_id=3, subject_name="S04").find_child(visit_id=3,
                                                                         visit_name="V03").parent().parent().satisfy(
        site_id=2, site_name="D02") is True
    assert len(root2.find_child(subject_id=3, subject_name="S04").children_index) == 1
    assert root2.find_child(subject_id=3, subject_name="S04").find_child(visit_id=1,
                                                                         visit_name="V01").parent().parent().satisfy(
        site_id=2, site_name="D03") is True
