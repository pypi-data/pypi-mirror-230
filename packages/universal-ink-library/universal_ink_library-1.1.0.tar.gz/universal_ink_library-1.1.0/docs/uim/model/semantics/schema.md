Module uim.model.semantics.schema
=================================

Classes
-------

`CommonRDF()`
:   Contains a list of used RDF types.

    ### Class variables

    `LOCALE: str`
    :

    `PRED_RDF_HAS_TYPE: str`
    :

`CommonViews(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Contains a list of known ink model views.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `CUSTOM_TREE`
    :

    `HWR_VIEW`
    :

    `LEGACY_HWR_VIEW`
    :

    `LEGACY_NER_VIEW`
    :

    `MAIN_INK_TREE`
    :

    `MAIN_SENSOR_TREE`
    :

    `NER_VIEW`
    :

    `SEGMENTATION_VIEW`
    :

`SemanticTriple(subject: str, predicate: str, obj: str)`
:   SemanticTriple
    ==============
    A semantic triple, or simply triple, is the atomic data entity data model.
    As its name indicates, a triple is a set of three entities that codifies a statement about semantic data in the
    form of subject predicate object expressions.
    
    Parameters
    ----------
    subject: str
        Subject
    predicate: str
        Predicate
    obj: str
        Object

    ### Instance variables

    `object: str`
    :   Object of the statement. (`str`)

    `predicate: str`
    :   Predicate of the statement. (`str`)

    `subject: str`
    :   Subject of the statement. (`str`)

`TripleStore(triple_statements: List[uim.model.semantics.schema.SemanticTriple] = None)`
:   TripleStore
    ===========
    
    Encapsulates a list of triple statements.
    
    Parameters
    ----------
    triple_statements: List[SemanticTriple]
        List of `SemanticTriple`s

    ### Instance variables

    `statements: List[uim.model.semantics.schema.SemanticTriple]`
    :   List of triple statements. (`List[SemanticTriple]`)

    ### Methods

    `add_semantic_triple(self, subject: str, predicate: str, obj: str)`
    :   Adding a semantic triple
        :param subject: subject of the statement
        :param predicate: predicate of the statement
        :param obj: object of the statement

    `all_statements_for(self, subject: str, predicate: str = None) ‑> List[uim.model.semantics.schema.SemanticTriple]`
    :   Returns all statements for a specific subject.
        
        Parameters
        ----------
        subject: `str`
            Filter for the subject URI
        predicate: `str`
            Predicate filter [optional]
        
        Returns
        -------
        statements: `List[SemanticTriple]`
            List of statements that match the filters.

    `append(self, triple_statement: uim.model.semantics.schema.SemanticTriple)`
    :   Appending the triple statement.
        
        Parameters
        ----------
        triple_statement: SemanticTriple
            Triple that needs to be added

    `clear_statements(self)`
    :   Remove all statements.

    `determine_sem_type(self, node: InkNode, typedef_pred: str = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type') ‑> Optional[str]`
    :   Determine the Semantic Type of node.
        
        Parameters
        ----------
        node: `InkNode`
            `InkNode` to extract the semantics from
        typedef_pred: `str`
            Predicate string
        
        Returns
        -------
        semantic_type: `str`
             Semantic type of the `InkNode`. None if the node is not found or the predicate statement.

    `filter(self, subject: Optional[str] = None, predicate: Optional[str] = None, obj: Optional[str] = None) ‑> List[uim.model.semantics.schema.SemanticTriple]`
    :   Returns all statements for a specific subject.
        
        Parameters
        ----------
        subject: `Optional[str]`
            Filter for the subject URI [optional]
        predicate: `Optional[str]`
            Predicate filter [optional]
        obj: `Optional[str]`
            Object filter [optional]
        
        Returns
        -------
        statements: `List[SemanticTriple]`
            List of statements that match the filters.

    `remove_semantic_triple(self, triple: uim.model.semantics.schema.SemanticTriple)`
    :   Removes a semantic triple from list.
        
        Parameters
        ----------
        triple: `SemanticTriple`
            Triple to be removed