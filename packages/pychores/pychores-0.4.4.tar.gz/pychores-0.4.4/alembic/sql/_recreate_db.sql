DROP DATABASE kinky_chores;
DROP DATABASE kinky_chores_tests;

DROP USER chores;

CREATE USER chores;
CREATE DATABASE kinky_chores WITH ENCODING 'UTF-8' LC_COLLATE='fr_FR.utf8' LC_CTYPE='fr_FR.utf8' TEMPLATE=template0 owner chores;
CREATE DATABASE kinky_chores_tests WITH ENCODING 'UTF-8' LC_COLLATE='fr_FR.utf8' LC_CTYPE='fr_FR.utf8' TEMPLATE=template0 owner chores;