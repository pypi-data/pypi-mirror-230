import unittest
from llmmanugen import Node


class TestNode(unittest.TestCase):

    counter = 0

    def setUp(self):
        self.root = Node("Root")
        self.child1 = Node("Child1")
        self.child2 = Node("Child2")
        self.grandchild1 = Node("Grandchild1")
        self.grandchild2 = Node("Grandchild2")
        TestNode.counter = Node.counter
        self.root.add_subnode(self.child1)
        self.root.add_subnode(self.child2)
        self.child1.add_subnode(self.grandchild1)
        self.child1.add_subnode(self.grandchild2)

    def test_dictionary_init(self):
        root = Node("Root")
        child1 = Node("Child1")
        grandchild1 = Node("Grandchild1")
        grandchild2 = Node("Grandchild2")
        child1.add_subnode(grandchild1)
        child1.add_subnode(grandchild2)
        root.add_subnode(child1)
        root.add_subnode({"title": "Child2"})
        child3 = Node("Child3", {"title": "Grandchild3"})
        root.add_subnodes(child3)

        self.assertEqual(type(root.subnodes[1]), Node)
        self.assertEqual(root.subnodes[1].title, "Child2")
        self.assertEqual(type(root.subnodes[2].subnodes[0]), Node)
        self.assertEqual(root.subnodes[2].subnodes[0].title, "Grandchild3")

    def test_counter(self):
        self.assertEqual(Node.counter, TestNode.counter)

    def test_init(self):
        node = Node("Test")
        self.assertEqual(node.title, "Test")
        self.assertEqual(node.parent, None)
        self.assertEqual(node.subnodes, [])
        self.assertEqual(node.current_node, None)
        self.assertEqual(node.reached_tree_end, False)
        self.assertEqual(node.reached_tree_start, True)
    
    def test_untitled_init(self):
        node = Node()
        self.assertIn("Node-", str(node))
    
    def test_fields(self):
        node = Node(**{"title": "Node", "subnodes": [], "foo": "bar"})
        self.assertEqual(node.fields, {"foo": "bar"})
        self.assertEqual(node.fields["foo"], "bar")
        # Shortcuts
        self.assertEqual(node["foo"], "bar")
        self.assertEqual(node.foo, "bar")
    
    def test_non_existing_attribute(self):
        node = Node()
        try:
            print("non_existing_attribute", node.non_existing_attribute)
        except AttributeError:
            pass
    
    def test_non_existing_key(self):
        node = Node()
        try:
            print("non_existing_key", node["non_existing_attribute"])
        except KeyError:
            pass

    def test_set_attr(self):
        node = Node(**{"foo": "bar"})
        self.assertEqual(node.fields["foo"], "bar")
        self.assertEqual(node["foo"], "bar")
        node["foo"] = "baz"
        self.assertEqual(node.fields["foo"], "baz")
        self.assertEqual(node["foo"], "baz")

    def test_set_item(self):
        node = Node(**{"foo": "bar"})
        self.assertEqual(node.fields["foo"], "bar")
        self.assertEqual(node.foo, "bar")
        node.foo = "bazz"
        self.assertEqual(node.fields["foo"], "bazz")
        self.assertEqual(node.foo, "bazz")

    def test_repr(self):
        node = Node(**{"subnodes": [Node()], "foo": "bar"})
        self.assertTrue("subnodes=1" in node.__repr__())

    def test_headless_nodes(self):
        root = Node()
        node1 = Node()
        node2 = Node()
        node1.add_subnode(node2)
        root.add_subnodes(node1)

        self.assertTrue("Node-" in root.__repr__())
        self.assertTrue("Node-" in root.subnodes[0].__repr__())
        self.assertTrue("Node-" in root.subnodes[0].subnodes[0].__repr__())

        root = Node("a", Node("b", Node("c")))
        self.assertTrue("llmmanugen.Node(a " in root.__repr__())
        self.assertTrue("llmmanugen.Node(b " in root.subnodes[0].__repr__())
        self.assertTrue("llmmanugen.Node(c " in root.subnodes[0].subnodes[0].__repr__())

        root = Node(Node(Node()))
        self.assertTrue(type(root.subnodes[0].subnodes[0]) is Node)

    def test_reset(self):
        self.root.reset()
        self.assertEqual(self.root.current_node, None)
        self.assertEqual(self.root.reached_tree_end, False)
        self.assertEqual(self.root.reached_tree_start, True)

    def test_is_at_tree_boundary(self):
        self.root.reset()
        self.assertTrue(self.root.is_at_tree_boundary())
        self.root.next()
        self.assertFalse(self.root.is_at_tree_boundary())

    def test_add_subnode(self):
        new_node = Node("NewNode")
        self.root.add_subnode(new_node)
        self.assertIn(new_node, self.root.subnodes)
        self.assertEqual(new_node.parent, self.root)

    def test_set_subnode(self):
        self.root.add_subnode(Node("Child3"))
        self.root.set_subnode(1, Node("Replaced"))
        self.assertEqual(self.root.subnodes[0].title, "Child1")
        self.assertEqual(self.root.subnodes[1].title, "Replaced")
        self.assertEqual(self.root.subnodes[2].title, "Child3")
    
    def test_insert_subnode(self):
        self.root.add_subnode(Node("Child3"))
        self.root.insert_subnode(1, Node("Inserted"))
        self.assertEqual(self.root.subnodes[0].title, "Child1")
        self.assertEqual(self.root.subnodes[1].title, "Inserted")
        self.assertEqual(self.root.subnodes[2].title, "Child2")
        self.assertEqual(self.root.subnodes[3].title, "Child3")

    def test_add_magic(self):
        node = Node() + Node() + Node()
        self.assertEqual(len(node.subnodes), 2)
        self.assertEqual(len(node.subnodes[0].subnodes), 0)
        self.assertEqual(len(node.subnodes[1].subnodes), 0)

        node = (Node() + Node()) + Node()
        self.assertEqual(len(node.subnodes), 2)
        self.assertEqual(len(node.subnodes[0].subnodes), 0)
        self.assertEqual(len(node.subnodes[1].subnodes), 0)

        node = Node() + (Node() + Node())

        self.assertEqual(len(node.subnodes), 1)
        self.assertEqual(len(node.subnodes[0].subnodes), 1)
        self.assertEqual(len(node.subnodes[0].subnodes[0].subnodes), 0)

        node = Node("a")
        node += Node("b")
        node + Node("c")
        self.assertEqual(len(node.subnodes), 2)

        # returns the last subnode
        node = Node("first") > Node("middle") > Node("last")  # node.parent.parent == Node() + (Node() + Node())
        self.assertEqual(node.title, "last")
        self.assertEqual(node.parent.title, "middle")
        self.assertEqual(node.parent.parent.title, "first")

        node = Node("first")
        node > Node("last")
        self.assertEqual(node.title, "first")
        self.assertEqual(node.subnodes[0].title, "last")

    def test_remove_magic(self):
        node = Node("a") + Node("b") + Node("c") + Node("d")
        self.assertEqual(len(node.subnodes), 3)
        node -= 1
        self.assertEqual(len(node.subnodes), 2)
        node -= 0
        self.assertEqual(len(node.subnodes), 1)
        self.assertTrue("llmmanugen.Node(d " in node.subnodes[0].__repr__())

        node = Node() + Node() - 0
        self.assertEqual(len(node.subnodes), 0)

    def test_next(self):
        self.root.reset()
        self.assertEqual(self.root.next(), self.root)
        self.assertEqual(self.root.next(), self.child1)
        self.assertEqual(self.root.next(), self.grandchild1)

    def test_prev(self):
        self.root.reset()
        self.root.next()
        self.root.next()
        self.assertEqual(self.root.prev(), self.root)
        self.assertEqual(self.root.prev(), None)

    def test_next_method(self):
        """
        Test to verify the behavior of the next method.
        """
        # Initial call should return the root itself
        self.assertEqual(self.root.next(), self.root)

        # Next call should return the first child
        self.assertEqual(self.root.next(), self.child1)

        # Next call should return the first grandchild
        self.assertEqual(self.root.next(), self.grandchild1)

        # Next call should return the second grandchild
        self.assertEqual(self.root.next(), self.grandchild2)

        # Next call should return the second child
        self.assertEqual(self.root.next(), self.child2)

        # Next call should return None (end of tree)
        self.assertEqual(self.root.next(), None)

    def test_prev_method(self):
        """
        Test to verify the behavior of the prev method.
        """
        # Move to the end of the tree
        while self.root.next():
            pass

        # Next call should return the second grandchild
        self.assertEqual(self.root.prev(), self.grandchild2)

        # Next call should return the first grandchild
        self.assertEqual(self.root.prev(), self.grandchild1)

        # Next call should return the first child
        self.assertEqual(self.root.prev(), self.child1)

        # Next call should return the root
        self.assertEqual(self.root.prev(), self.root)

        # Next call should return None (start of tree)
        self.assertEqual(self.root.prev(), None)

    def test_parent_property(self):
        self.assertEqual(self.child1.parent, self.root)
        self.assertEqual(self.grandchild1.parent, self.child1)

    def test_set_get_current_node_by_index(self):
        self.root.set_current_node_by_index([0, 1])
        self.assertEqual(self.root.get_current_node_index(), [0, 1])

    def test_set_current_node_by_index(self):
        """
        Test to verify the behavior of the set_current_node_by_index method.
        """
        # Set current node to root using an empty list and verify
        self.root.set_current_node_by_index([])
        self.assertEqual(self.root.current_node, self.root)  # 1

        # Set current node to first child of root and verify
        self.root.set_current_node_by_index([0])
        self.assertEqual(self.root.current_node, self.child1)  # 2

        # Set current node to second grandchild of first child and verify
        self.root.set_current_node_by_index([0, 1])
        self.assertEqual(self.root.current_node, self.grandchild2)  # 3

    def test_get_node_by_index(self):
        """
        Test to verify the behavior of the get_node_by_index method.
        """
        # Get root node using an empty list and verify
        node = self.root.get_node_by_index([])  # 1
        self.assertEqual(node, self.root)

        # Get first child of root and verify
        node = self.root.get_node_by_index([0])  # 2
        self.assertEqual(node, self.child1)

        # Get second grandchild of first child and verify
        node = self.root.get_node_by_index([0, 1])  # 3
        self.assertEqual(node, self.grandchild2)

    def test_set_current_node_by_index_over_index(self):
        """
        Test to verify the behavior of the set_current_node_by_index method with an out-of-bounds index.
        """
        # Attempt to set current node using an out-of-bounds index
        with self.assertRaises(IndexError):
            self.root.set_current_node_by_index([999])

    def test_get_node_by_index_over_index(self):
        """
        Test to verify the behavior of the get_node_by_index method with an out-of-bounds index.
        """
        # Attempt to get a node using an out-of-bounds index
        with self.assertRaises(IndexError):
            self.root.get_node_by_index([999])

    def test_get_root_and_target(self):
        """
        This test method verifies the behavior of get_root_and_target in various scenarios.
        """
        # Scenario 1: Invoke from root, default parameter (True)
        # According to docstring logic point 1, the root and target should be the root itself
        # as there's no parent for root.
        self.root.next()
        root, target = self.root.get_root_and_target()
        self.assertEqual(root, self.root)
        self.assertEqual(target, self.root)

        # Scenario 2: Invoke from child1, default parameter (True)
        # According to docstring logic point 1, the root should be the root of the entire tree,
        # and the target should be the root's current node.
        self.root.next()
        root, target = self.child1.get_root_and_target()
        self.assertEqual(root, self.root)
        self.assertEqual(target, self.child1)

        # Scenario 3: Invoke from grandchild1, default parameter (True)
        # According to docstring logic point 1, the root should be the root of the entire tree,
        # and the target should be the root's current node.
        self.root.next()
        root, target = self.grandchild1.get_root_and_target()
        self.assertEqual(root, self.root)
        self.assertEqual(target, self.grandchild1)

        # Scenario 4: Invoke from root, with parameter False
        # According to docstring logic point 2, the root and target should be the root itself
        # as there's no parent for root.
        self.root.reset()
        self.root.next()
        root, target = self.root.get_root_and_target(from_root=False)
        self.assertEqual(root, self.root)
        self.assertEqual(target, self.root)

    def test_get_root_and_target2(self):
        # Scenario 5: Invoke from child1, with parameter False
        # According to docstring logic point 2, the root should be child1,
        # and the target should be None due to unexisting target in the child1 branch.
        child1, target = self.child1.get_root_and_target(from_root=False)
        self.assertEqual(child1, self.child1)
        self.assertEqual(target, None)

        self.root.next()
        self.root.next()
        child1, target = self.child1.get_root_and_target(from_root=False)
        self.assertEqual(child1, self.child1)
        self.assertEqual(target, self.child1)

        # Scenario 6: Invoke from grandchild1, with parameter False
        # According to docstring logic point 2, the root should be grandchild1,
        # and the target should be None due to unexisting target in the grandchild1 branch.
        grandchild1, target = self.grandchild1.get_root_and_target(from_root=False)
        self.assertEqual(grandchild1, self.grandchild1)
        self.assertEqual(target, self.child1)

        self.root.next()
        grandchild1, target = self.grandchild1.get_root_and_target(from_root=False)
        self.assertEqual(grandchild1, self.grandchild1)
        self.assertEqual(target, self.grandchild1)

    def test_get_current_node_index(self):
        """
        This test method verifies the behavior of get_current_node_index in various scenarios.
        """
        # Scenario 1: Invoke from root, default parameter (True)
        # As per docstring, the path should be empty as we are at the root.
        self.root.next()
        path = self.root.get_current_node_index()
        self.assertEqual(path, [])  # 1

        # Scenario 2: Invoke from root, default parameter (True)
        # Path should be [0] as child1 is the first child of the root.
        self.root.next()
        path = self.root.get_current_node_index()
        self.assertEqual(path, [0])  # 2

        # Scenario 3: Invoke from root, default parameter (True)
        # Path should be [0, 0] as grandchild1 is the first child of the first child of the root.
        self.root.next()
        path = self.root.get_current_node_index()
        self.assertEqual(path, [0, 0])  # 3

        # Scenario 4: Invoke from root, with parameter False
        # The path should be empty as we are at the root.
        path = self.root.get_current_node_index(from_root=False)
        self.assertEqual(path, [0, 0])  # 4

        # Scenario 5: Invoke from child1, with parameter False
        # Path should be [] as child1 is the root in this context.
        path = self.child1.get_current_node_index(from_root=False)
        self.assertEqual(path, [0])  # 5

        # Scenario 6: Invoke from grandchild1, with parameter False
        # Path should be [0] as grandchild1 is the first child of child1 in this context.
        path = self.grandchild1.get_current_node_index(from_root=False)
        self.assertEqual(path, [])  # 6

        # Scenario 7: Invoke from root, default parameter (True)
        # As per docstring, the path should be empty as we are at the root.
        self.root.reset()
        self.root.next()
        path = self.root.get_current_node_index()
        self.assertEqual(path, [])  # 7

        # Scenario 8: Invoke from child1, default parameter (True)
        # Path should be [0] as child1 is the first child of the root.
        self.root.next()
        path = self.child1.get_current_node_index()
        self.assertEqual(path, [0])  # 8

        # Scenario 9: Invoke from grandchild1, default parameter (True)
        # Path should be [0, 0] as grandchild1 is the first child of the first child of the root.
        self.root.next()
        path = self.grandchild1.get_current_node_index()
        self.assertEqual(path, [0, 0])  # 9

    def test_get_root_node(self):
        """
        Test to verify the behavior of the get_root_node method.
        """
        # Invoking from the root should return the root itself
        self.assertEqual(self.root.get_root_node(), self.root)

        # Invoking from a child should return the ultimate root
        self.assertEqual(self.child1.get_root_node(), self.root)

        # Invoking from a grandchild should return the ultimate root
        self.assertEqual(self.grandchild1.get_root_node(), self.root)

    def test_get_last_node(self):
        """
        Test to verify the behavior of the get_last_node method.
        """
        # Invoking from the root should return the last child
        self.assertEqual(self.root.get_last_node(), self.child2)

        # Invoking from a child with subnodes should return the last subnode
        self.assertEqual(self.child1.get_last_node(), self.grandchild2)

        # Invoking from a child without subnodes should return None
        self.assertEqual(self.child2.get_last_node(), None)

    def test_get_end_node(self):
        """
        Test to verify the behavior of the get_end_node method.
        """
        # Invoking from the root with default parameter should return the deepest last node
        self.assertEqual(self.root.get_end_node(), self.child2)

        # Invoking from a child with default parameter should return the deepest last node within the child's subtree
        self.assertEqual(self.child1.get_end_node(), self.grandchild2)

        # Invoking from the root with parameter False should return the last node of the root
        self.assertEqual(self.child1.get_end_node(from_root=True), self.child2)

    def test_pretty_print(self):
        print("Test pretty_print output:")
        self.root.pretty_print()

    def test_next_method_called_by_subnode(self):
        """
        Test to verify the behavior of the next method when called by a subnode.
        """
        # Set current node to first child
        self.child1.next()

        # First call should yield the current node
        self.assertEqual(self.child1.current_node, self.child1)

        # First call should return the first grandchild
        self.assertEqual(self.child1.next(), self.grandchild1)

        # Next call should return the second grandchild
        self.assertEqual(self.child1.next(), self.grandchild2)

        # Next call should return None (end of subtree)
        self.assertEqual(self.child1.next(), None)

        self.child1.reset()

        # First call should yield the current node
        self.assertEqual(self.child1.current_node, None)

        # First call should return the first grandchild
        self.assertEqual(self.child1.next(), self.child1)

    def test_prev_method_called_by_root(self):
        """
        Test to verify the behavior of the prev method when called by a subnode.
        """
        # Move to the end of the subtree rooted at first child
        while self.root.next():
            pass

        # First call should return the second grandchild
        self.assertEqual(self.root.prev(), self.grandchild2)

        # Next call should return the first grandchild
        self.assertEqual(self.root.prev(), self.grandchild1)

        # Next call should return None (start of subtree)
        self.assertEqual(self.root.prev(), self.child1)

        # Next call should return None (start of subtree)
        self.assertEqual(self.root.prev(), self.root)

        # Next call should return None (start of subtree)
        self.assertEqual(self.root.prev(), None)

    def test_prev_method_called_by_subnode(self):
        """
        Test to verify the behavior of the prev method when called by a subnode.
        """
        # Move to the end of the subtree rooted at first child
        while self.child1.next():
            pass

        # First call should return the first grandchild
        self.assertEqual(self.child1.prev(), self.grandchild1)

        # Next call should return the first grandchild
        self.assertEqual(self.child1.prev(), self.child1)

        # Next call should return None (start of subtree)
        self.assertEqual(self.child1.prev(), None)

    def test_next_method_independence_within_tree(self):
        """
        Test to verify that calling next on different subnodes within the same tree works independently.
        """
        self.root.next()
        # First call for root should return the first child
        self.assertEqual(self.root.next(), self.child1)

        self.child1.next()
        # First call for child1 should return the first grandchild
        self.assertEqual(self.child1.next(), self.grandchild1)

        # Second call for root should return the second child
        self.assertEqual(self.root.next(), self.grandchild1)

        # Second call for child1 should return the second grandchild
        self.assertEqual(self.child1.next(), self.grandchild2)

    def test_next_prev_method_independence_within_tree(self):
        """
        Test to verify that calling next and prev on different subnodes within the same tree works independently.
        """
        # Navigate to the end of the tree for both root and child1
        while self.root.next():
            pass
        while self.child1.next():
            pass

        # First prev call for root should return the second child
        self.assertEqual(self.root.current_node, self.child2)

        # First prev call for child1 should return the second grandchild
        self.assertEqual(self.child1.current_node, self.grandchild2)

        # First prev call for root should return the second child
        self.assertEqual(self.root.prev(), self.grandchild2)

        # First prev call for child1 should return the second grandchild
        self.assertEqual(self.child1.prev(), self.grandchild1)

        # Second prev call for root should return the first child
        self.assertEqual(self.root.prev(), self.grandchild1)

        # Second prev call for child1 should return the first grandchild
        self.assertEqual(self.child1.prev(), self.child1)

    def test_next_prev_boundary_behavior(self):
        """
        Test to verify that next and prev methods correctly set boundary flags and that
        is_at_tree_boundary method works as expected.
        """
        # Initially, is_at_tree_boundary should return True for start boundary
        self.assertTrue(self.root.is_at_tree_boundary())

        # Navigate to the end of the tree for root
        while self.root.next():
            pass

        # Now, is_at_tree_boundary should return True for end boundary
        self.assertTrue(self.root.is_at_tree_boundary())

        # Navigate back to the start of the tree for root
        while self.root.prev():
            pass

        # is_at_tree_boundary should return True again for start boundary
        self.assertTrue(self.root.is_at_tree_boundary())

        # Test the same for child1 (subnode)
        self.assertTrue(self.child1.is_at_tree_boundary())

        # Navigate to the end of the subtree for child1
        while self.child1.next():
            pass

        # Now, is_at_tree_boundary should return True for end boundary
        self.assertTrue(self.child1.is_at_tree_boundary())

        # Navigate back to the start of the subtree for child1
        while self.child1.prev():
            pass

        # is_at_tree_boundary should return True again for start boundary
        self.assertTrue(self.child1.is_at_tree_boundary())

    def test_prev_cant_access_root_from_child(self):
        """
        Test to verify that calling prev on a child node does not allow traversing up to the root.
        """
        # Navigate to the end of the subtree for child1
        while self.child1.next():
            pass

        # Try to navigate back up, should not reach the root
        node = self.child1
        while node:
            node = node.prev()
            self.assertNotEqual(node, self.root)

    def test_next_cant_access_sibling(self):
        """
        Test to verify that calling next on a child node does not allow traversing to its sibling.
        """
        # Navigate to the end of the subtree for child1
        while self.child1.next():
            pass

        # Try to navigate forward, should not reach the child2
        node = self.child1
        while node:
            node = node.next()
            self.assertNotEqual(node, self.child2)

    def test_remove_specific_node(self):
        # Test removing a specific node
        self.root.remove([0, 1])  # Should remove grandchild2 under child1
        self.assertEqual(len(self.root.subnodes[0].subnodes), 1)  # child1 should now have 1 subnode
        self.assertEqual(self.root.subnodes[0].subnodes[0]._title, "Grandchild1")  # Remaining subnode should be grandchild1

    def test_remove_all_subnodes(self):
        # Test removing all subnodes of a node
        self.root.remove()  # Should remove both child1 and child2
        self.assertEqual(len(self.root.subnodes), 0)  # Root should have no subnodes

    def test_remove_with_invalid_indices(self):
        # Test removing with invalid index
        with self.assertRaises(IndexError):
            self.root.remove([0, 10])  # Invalid index

    def test_remove_with_empty_indices(self):
        # Test removing with empty index list, should act like remove()
        self.root.remove([])  # Should remove both child1 and child2
        self.assertEqual(len(self.root.subnodes), 0)  # Root should have no subnodes

    def test_remove_subnodes_single_indices(self):
        # Creating a simple tree structure
        root = Node("Root")
        child1 = Node("Child1")
        child2 = Node("Child2")
        child3 = Node("Child3")
        root.add_subnodes(child1, child2, child3)

        # Removing nodes at indices 0 and 2
        root.remove_subnodes([0, 2])

        # Verifying the tree structure after removal
        remaining_titles = [node.title for node in root.subnodes]
        self.assertEqual(remaining_titles, ["Child2"])

    def test_remove_subnodes_nested_indices(self):
        # Creating a nested tree structure
        root = Node("Root")
        child1 = Node("Child1")
        child2 = Node("Child2")
        grandchild1 = Node("Grandchild1")
        grandchild2 = Node("Grandchild2")
        child1.add_subnodes(grandchild1, grandchild2)
        root.add_subnodes(child1, child2)

        # Removing nodes at nested indices [0, 0] and [0, 1]
        root.remove_subnodes([[0, 0], [0, 1]])

        # Verifying the tree structure after removal
        remaining_titles = [node.title for node in root.get_node_by_index([0]).subnodes]
        self.assertEqual(remaining_titles, [])

    def test_remove_subnodes_mixed_indices(self):
        # Creating a nested tree structure
        root = Node("Root")
        child1 = Node("Child1")
        child2 = Node("Child2")
        grandchild1 = Node("Grandchild1")
        grandchild2 = Node("Grandchild2")
        child1.add_subnodes(grandchild1, grandchild2)
        root.add_subnodes(child1, child2)

        # Removing nodes at mixed indices [0, 1] and 1
        root.remove_subnodes([[0, 1], 1])

        # Verifying the tree structure after removal
        remaining_child_titles = [node.title for node in root.subnodes]
        self.assertEqual(remaining_child_titles, ["Child1"])

        remaining_grandchild_titles = [node.title for node in root.get_node_by_index([0]).subnodes]
        self.assertEqual(remaining_grandchild_titles, ["Grandchild1"])

    def test_iteration(self):
        expected_titles = ["Root", "Child1", "Grandchild1", "Grandchild2", "Child2"]
        # First round
        result_titles = [node.title for node in self.root]
        self.assertEqual(expected_titles, result_titles)
        # Second round
        self.root.reset()
        result_titles = [node.title for node in self.root]
        self.assertEqual(expected_titles, result_titles)

    def test_stop_iteration(self):
        iterator = iter(self.root)
        for _ in self.root:
            pass  # Traverse the entire tree
        with self.assertRaises(StopIteration):
            next(iterator)

    def test_has_subnodes(self):
        root = Node("Root")
        child1 = Node("Child1")
        child2 = Node("Child2")
        grandchild1 = Node("Grandchild1")
        grandchild2 = Node("Grandchild2")
        child1.add_subnodes(grandchild1, grandchild2)
        root.add_subnodes(child1, child2)
        self.assertEqual((True, True, False), (root.has_subnodes(), child1.has_subnodes(), child2.has_subnodes()))

    def test_search(self):
        root = Node("Root")
        child1 = Node("Child1")
        child2 = Node("Child2")
        grandchild1 = Node("Grandchild")
        grandchild2 = Node("Grandchild")
        child1.add_subnodes(grandchild1, grandchild2)
        root.add_subnodes(child1, child2)

        result = root.search("Grandchild")
        self.assertEqual(result[0][0].title, "Grandchild")
        self.assertEqual(result[0][1], [0, 0])
        self.assertEqual(result[1][1], [0, 1])
        self.assertEqual(len(result), 2)

    def test_find_by_titles(self):
        root = Node("Root")
        child1 = Node("Child1")
        child2 = Node("Child2")
        grandchild1 = Node("Grandchild")
        grandchild2 = Node("Grandchild")
        child1.add_subnodes(grandchild1, grandchild2)
        root.add_subnodes(child1, child2)

        result = root.find_path_by_titles("Child1")
        self.assertEqual(result[0][0].title, "Child1")
        self.assertEqual(result[0][1], [0])

        result = root.find_path_by_titles(["Child1", "Grandchild"])
        self.assertEqual(result[0][0].title, "Grandchild")
        self.assertEqual(result[0][1], [0, 0])
        self.assertEqual(result[1][1], [0, 1])
