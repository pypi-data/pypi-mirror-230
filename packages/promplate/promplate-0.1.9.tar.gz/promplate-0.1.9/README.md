# Promplate

> _Promplate_ is for **promp**t + tem**plate**

I want to build a cross-language prompt engineering framework.

## IDE Support 🌹

I try to make the syntax compatible with `Jinja2`.

## Future Features (or TODOs?)

- [x] (lazy) template compiling
- [x] support any evaluatable expression inside template like `{{ [ i for i in range(n) ] }}`
- [ ] create documentation
- [ ] javascript implementation
- [ ] support chains and agents
- [ ] error handling
- [ ] template rich printing
- [x] implement component syntax `{% Component * arg1 arg2 kwarg1=1 kwarg2=2 **kwargs %}`
- [ ] allow more corner cases for the component syntax
  - [ ] `{% Componnet arg=" * " %}`
  - [ ] `{% Componnet arg = " * " %}`
  - [ ] `{% Componnet arg = await f()`
- [ ] if the outer context is a `defaultdict`, the context passing to component should be?
  - or maybe this should be determined by the component itself
  - because a component could be a `Node` and a `Node` can have preprocesses
- [ ] support while loop and isolated variable declaration
- [x] `else` and `elif` tag
- [ ] directory based routing
- [ ] caching (and cache-controls maybe?)
- [x] implement more [loaders](https://jinja.palletsprojects.com/api/#loaders)
  - for now you can load template from local filesystem or urls
- [x] multi-file chat template
  - using components
