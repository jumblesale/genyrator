from sqlalchemy import BigInteger
from sqlalchemy.dialects import postgresql, mysql, sqlite

# sqlite does not allow BigIntegers as a auto-incrementing primary key
BigIntegerVariantType = BigInteger()
BigIntegerVariantType = BigIntegerVariantType.with_variant(postgresql.BIGINT(), 'postgresql')
BigIntegerVariantType = BigIntegerVariantType.with_variant(mysql.BIGINT(), 'mysql')
BigIntegerVariantType = BigIntegerVariantType.with_variant(sqlite.INTEGER(), 'sqlite')
