{ buildPythonPackage
, fetchFromGitHub
, lib
, httpx
, poetry-core
, requests
, websockets
, websocket-client
}:

buildPythonPackage rec {
  pname = "polygon-api-client";
  version = "1.15.3";
  format = "pyproject";

  src = fetchFromGitHub {
    owner = "polygon-io";
    repo = "client-python";
    rev = "6ca3fc30726c2db139e874438933f3533257c615";
    hash = "sha256-/yrOlqJgGG7EVp0zvKnUPj9aIq1hSxcvFVTwCBoQM6Q=";
  };

  nativeBuildInputs = [
    poetry-core
  ];

  dependencies = [
    httpx
    requests
    websockets
    websocket-client
  ];

  meta = {
    description = "A Complete Python Wrapper for Polygon.io APIs.";
    homepage = "https://github.com/polygon-io/client-python";
    license = lib.licenses.mit;
    maintainers = [
      # lib.maintainers.pssolanki111
    ];
  };
}