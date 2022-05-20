import os

from pathlib import Path
from unittest import TestCase

from pyparsing import ParserElement

from pydbml import PyDBML


ParserElement.set_default_whitespace_chars(' \t\r')


TEST_DATA_PATH = Path(os.path.abspath(__file__)).parent / 'test_data'


class EditingTestCase(TestCase):
    def setUp(self):
        self.dbml = PyDBML(TEST_DATA_PATH / 'editing.dbml')


class TestEditTable(EditingTestCase):
    def test_name(self) -> None:
        products = self.dbml['public.products']
        products.name = 'changed_products'
        self.assertIn('CREATE TABLE "changed_products"', products.sql)
        self.assertIn('CREATE INDEX "product_status" ON "changed_products"', products.sql)
        self.assertIn('Table "changed_products"', products.dbml)

        ref = self.dbml.refs[0]
        self.assertIn('ALTER TABLE "changed_products"', ref.sql)
        self.assertIn('"changed_products"."merchant_id"', ref.dbml)

        index = products.indexes[0]
        self.assertIn('ON "changed_products"', index.sql)

    def test_alias(self) -> None:
        products = self.dbml['public.products']
        products.alias = 'new_alias'

        self.assertIn('as "new_alias"', products.dbml)


class TestColumn(EditingTestCase):
    def test_name(self) -> None:
        products = self.dbml['public.products']
        col = products['name']
        col.name = 'new_name'
        self.assertEqual(col.sql, '"new_name" varchar')
        self.assertEqual(col.dbml, '"new_name" varchar')
        self.assertIn('"new_name" varchar', products.sql)
        self.assertIn('"new_name" varchar', products.dbml)

        self.assertEqual(col, products[col.name])

    def test_name_index(self) -> None:
        products = self.dbml['public.products']
        col = products['status']
        col.name = 'changed_status'
        self.assertIn('"changed_status"', products.indexes[0].sql)
        self.assertIn('changed_status', products.indexes[0].dbml)
        self.assertIn(
            'CREATE INDEX "product_status" ON "products" ("merchant_id", "changed_status");',
            products.sql
        )
        self.assertIn(
            "(merchant_id, changed_status) [name: 'product_status']",
            products.dbml
        )

    def test_name_ref(self) -> None:
        products = self.dbml['public.products']
        col = products['merchant_id']
        col.name = 'changed_merchant_id'
        merchants = self.dbml['public.merchants']
        table_ref = merchants.get_refs()[0]
        self.assertIn('FOREIGN KEY ("changed_merchant_id")', table_ref.sql)


class TestEnum(EditingTestCase):
    def test_enum_name(self):
        products = self.dbml['public.products']
        enum = self.dbml.enums[0]
        enum.name = 'changed product status'
        self.assertIn('CREATE TYPE "changed product status"', enum.sql)
        self.assertIn('Enum "changed product status"', enum.dbml)

        col = products['status']
        self.assertEqual(col.sql, '"status" "changed product status"')
        self.assertEqual(col.dbml, '"status" "changed product status"')
