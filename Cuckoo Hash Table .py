"""
Cuckoo Hash Table Implementation

Implements a hash table which utilises `CuckooHashing` to place elements into
the table.
"""

from linear_hash import LinearHashFunction
from TableEntry import TableEntry
import HashTableInterface

from functools import reduce


class CuckooHashTable(HashTableInterface.HashTableInterface):
    def __init__(self, m, prng_one, prng_two):
        """
        Initialises the table with the correct hashes.
        :param m: The size of the table.
        :param h1n: The first variant of the hash.
        :param h2n:  The second variant of the hash.
        :param prng_one: Seeded Pseudo Random Number Generator for h1.
        :param prng_two: Seeded Pseudo Random Number Generator for h2.
        """

        self.size = m
        self.h1 = LinearHashFunction(m, prng_one)
        self.h2 = LinearHashFunction(m, prng_two)
        self.table = [None for i in range(0, m)]
        self.M = m

    def __repr__(self):
        s = "[{}]".format(
            reduce(
                (lambda a, b: "{}{}".format(a, b)),
                map(lambda x: "-" if x is None else x.get_value(), self.table)
            )
        )
        return s

    def _check_success(self, k, v):
        """
        Runs through the put to check if there's an empty spot
        :return: Boolean if can succeed.
        """

        count = 0
        current = k
        hash_to_use = self.h1
        next = None

        while count < self.size:

            # Check if empty
            if self.table[hash_to_use(current)] is None:
                return True
            else:
                next = self.table[hash_to_use(current)].get_key()

                # Find the hash to use.
                if self.h1(next) == hash_to_use(current):
                    hash_to_use = self.h2
                else:
                    hash_to_use = self.h1
                current = next
                count += 1

        return False

    def put(self, k, v):
        """
        Puts the value into an entry into the table.
        :param k: The key for the matching value.
        :param v: The value to place into the table.
        """
        # Base Case - H1(K) empty or H2(K) empty.
        if self.table[self.h1(k)] is None or self.table[self.h1(k)].get_key() == k:
            # Add or Update the new entry
            self.table[self.h1(k)] = TableEntry(k, v)
            return True
        elif self.table[self.h2(k)] is None or self.table[self.h2(k)].get_key() == k:
            # Add or Update the new entry
            self.table[self.h2(k)] = TableEntry(k, v)
            return True

        # Check if they are actually equal
        if not(self._check_success(k, v)):
            return False

        cache = self.table.copy()
        current = TableEntry(k, v)
        hash_to_use = self.h1
        next = None
        count = 0

        while count < self.size:
            # Check if empty
            if self.table[hash_to_use(current.get_key())] is None:
                self.table[hash_to_use(current.get_key())] = current
                return True
            else:
                next = self.table[hash_to_use(current.get_key())]
                self.table[hash_to_use(current.get_key())] = current

                # Find the hash to use.
                if self.h1(next.get_key()) == hash_to_use(current.get_key()):
                    hash_to_use = self.h2
                else:
                    hash_to_use = self.h1
                current = next
                count += 1

        return False

    def get(self, key):
        """
        Get the element with the key from the table
        :param key: The key of the element to fetch
        :return: The value to return. OR -1 if not found
        """

        if self.table[self.h1(key)] is not None and self.table[self.h1(key)].k == key:
            return self.table[self.h1(key)].v
        elif self.table[self.h2(key)] is not None and self.table[self.h2(key)].k == key:
            return self.table[self.h2(key)].v
        return -1

    def remove(self, key):
        """
        Remove the element from the table.
        :param key: The key of the element to remove.
        :return: The VALUE associated to the entry that was removed.
            -1 if the entry could not be found
        """
        ret = -1
        h1k = self.h1(key)
        h2k = self.h2(key)
        if self.table[h1k] is not None:
            if self.table[h1k].k == key:
                ret = self.table[h1k].v
                self.table[h1k] = None
        elif self.table[h2k] is not None:
            if self.table[h2k].k == key:
                ret = self.table[h2k].v
                self.table[h2k] = None

        return ret