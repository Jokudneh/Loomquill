select
    order_id,
    sum(amount) as total_amount
from {{ ref('orders' )}}
