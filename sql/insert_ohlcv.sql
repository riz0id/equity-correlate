-- !!!
-- NOT CURRENTLY IN USE
-- !!!

INSERT INTO ohlcv (
  t, -- timestamp as a UNIX epoch in minutes
  s, -- symbol
  o, -- open
  h, -- high
  l, -- low
  c, -- close
  v  -- volume
) VALUES (?, ?, ?, ?, ?, ?, ?)