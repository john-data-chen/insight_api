from flask.ext.sqlalchemy import SQLAlchemy 


class UnLockedAlchemy(SQLAlchemy):
    def apply_driver_hacks(self, app, info, options):
        if not "isolation_level" in options:
            options["isolation_level"] = "READ UNCOMMITTED"  # For example
        return super(UnLockedAlchemy, self).apply_driver_hacks(app, info, options)


class nullpool_SQLAlchemy(UnLockedAlchemy): 
      def apply_driver_hacks(self, app, info, options): 
              super(nullpool_SQLAlchemy, self).apply_driver_hacks(app, info, options) 
              from sqlalchemy.pool import NullPool 
              options['poolclass'] = NullPool 
              del options['pool_size']
 
"""
db = nullpool_SQLAlchemy()
db = nullpool_SQLAlchemy()
"""
