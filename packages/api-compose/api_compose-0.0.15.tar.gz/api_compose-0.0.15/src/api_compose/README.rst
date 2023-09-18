
.. graphviz::

   digraph example {
       services -> core;
       root -> core;
       root -> services;
       manifests -> core;
       manifests -> root;
       cli -> core;
       cli -> manifests;
   }


Core
======================

- Core Utilities

Services
======================

- Loosely coupled services which use models as APIs

Root
======================

- Composition Root of the services

Manifests
======================

- Json/Dict Representation of Models. Include propcessing logic to transform to models.


CLI
======================

- CLI to interact with the programme
