# --SELECT users.username, user_accounts.id as account_id, orders.id as order_id, order_items.quantity as quantity, services.name as service_name
# --FROM users
# --JOIN user_accounts ON user_accounts.user_id = users.id
# --JOIN orders ON orders.account_id = user_accounts.id
# --JOIN order_items ON order_items.order_id = orders.id
# --JOIN services ON order_items.service_id = services.id;
#
#
# -- transaction amount calculation
# --"""
# --SELECT SUM(total)
# --FROM (SELECT quantity * services.price as total
# --FROM order_items
# --JOIN services on services.id = order_items.service_id
# --WHERE order_items.order_id = 5) as subquery;
# --"""
#
#
# -- from ReportsService
# -- _calculate_revenue_from_services:
# --# services_with_revenues_in_the_period = (
# --#     self.db_session.query(
# --#         tables.Service.name,
# --#         sa.func.sum(tables.OrderItem.quantity * tables.Service.price)
# --#     )
# --#     .join(tables.Order, tables.Order.id == tables.OrderItem.order_id)
# --#     .join(tables.Transaction, tables.Transaction.order_id == tables.Order.id)
# --#     .join(tables.Service, tables.OrderItem.service_id == tables.Service.id)
# --#     .where(
# --#         sa.and_(tables.Order.status == "COMPLETED",
# --#                 tables.Transaction.date.date() >= reporting_period_start,
# --#                 tables.Transaction.date.date() <= reporting_period_end),
# --#     )
# --#     .group_by(tables.Service.name)
# --#     .all()
# --# )
# --
# ---- TransactionsService
# ---- _calculate_transaction_amount:
# --# transaction_amount = self.db_session.query(
# --#         sa.func.sum(tables.OrderItem.quantity * tables.Service.price))\
# --#         .join(tables.Service, tables.OrderItem.service_id == tables.Service.id)\
# --#         .filter(tables.OrderItem.order_id == order_id)\
# --#         .scalar()
#
#
# -- ReportsService - get_account_transactions_info()
# --account_transactions = self.db_session.query(
# --            tables.Transaction)\
# --            .filter(
# --            sa.or_(
# --                tables.Transaction.from_user_id == user_id,
# --                tables.Transaction.to_user_id == user_id,
# --                tables.Transaction.order_id.in_(user_account_order_ids)
# --            )
# --        )
#
# -- TransactionsService
# --def _get_transaction_by_order_id
# --        # transaction = (
# --        #     self.db_session.query(tables.Transaction)
# --        #     .where(
# --        #         sa.and_(
# --        #             (
# --        #                 tables.Transaction.order_id == order_id,
# --        #                 tables.Transaction.type == type_,
# --        #             )
# --        #         )
# --        #     )
# --        #     .first()
# --        # )
#
# -- InformationService
# -- _get_user_accounts_by_order_id
# --        # regular_account = (
# --        #     self.db_session
# --        #         .query(tables.UserAccount)
# --        #         # orders are linked to regular accounts only - should be implemented in orders microservice
# --        #         .join(tables.Order, tables.UserAccount.id == tables.Order.account_id)
# --        #         .filter(
# --        #             tables.Order.id == order_id,
# --        #         )
# --        #     .first()
# --        # )
# --        #
# --        # reserve_account = self.db_session\
# --        #     .query(tables.UserAccount)\
# --        #     .filter(sa.and_(
# --        #         tables.UserAccount.user_id == regular_account.user_id,
# --        #         tables.UserAccount.type == AccountType.RESERVE
# --        #     )).first()
