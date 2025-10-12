$TTL 3600
@   IN  SOA ns1.example.com. hostmaster.example.com. (
        2025101201 ; serial
        3600       ; refresh
        1800       ; retry
        604800     ; expire
        3600       ; minimum
)
    IN  NS  ns1.example.com.
ns1 IN  A   192.0.2.53
www IN  A   192.0.2.80
