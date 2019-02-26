# TODO
remaining tasks for the `0.2` release, in order of priority

* [ ] move behaviours (getting, updating, etc.) to library methods
* [ ] validation (schema, column, relationship)
* [ ] declarative entity definitions
* [ ] schema validation
* [ ] documentation
* [ ] callbacks
* [ ] pagination
* [ ] hateoas-style support

## move behaviours
at the moment, when you generate your code, a lot of functionality
gets put in the restplus endpoint. this results in huge diffs between
versions and is tiresome to test.

it is proposed that this code moves into a library function which then
gets imported by the endpoint. this will make the code easier to test,
and will result in a smaller generated codebase.

## validation
there's loads that could be done to validate a schema. the most interesting
part is probably the relationships - to do this we would need a two-pass
implementation where the first pass builds up an idea of what entities are
present and how they relate to one another, and the second pass
verifies that these relationships are possible.

error reporting should be as approachable and helpful as possible. see
[elm](https://elm-lang.org/) for inspiration.

## declarative entity definitions
writing entities declaratively is much more natural to python developers
already familiar with sqlalchemy, which is a dependency of genyrator.
it is proposed to use decorators in the style of
[attr.s](http://www.attrs.org/en/stable/) to configure the behaviour of
entities.

## schema validation
we currently validate provided data with a really old version
of marhsmallow-sqlalchemy. pros: it gives nice errors and will persist
the data if it's valid. cons: it's not easily configurable from the standpoint
of someone writing an entity. explore going with a different library, writing our
own or something different? there could be the opportunity to allow the option
to specify column-level validation - how would this look?


## callbacks
provide a mechanism for intercepting the data at different points of processing.
perhaps as a first pass, just allow a user-provided method to be called at the start
of the endpoint method, and another before the response gets serialized?


## documentation

it would be wonderful to have documentation which takes the time to explain
some of the core concepts of columns, entities and schemas, as well as
giving examples of how to configure different kinds of relationships.

## pagination
configurable pagination on a per-endpoint basis.  

## hateoas-style support
location headers. explorable links.
