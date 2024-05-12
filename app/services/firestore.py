from fastapi import HTTPException
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from services.gcp import access_secret_file, setup_logger
import json

logger = setup_logger(__name__)

def initialize_firestore():
    try:
        if not firebase_admin._apps:
            # Initialize Firestore if not already initialized
            secret_content = access_secret_file("firebase-key")
            service_account_info = json.loads(secret_content)
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            logger.info("Firestore initialized")
        return db
    except Exception as e:
        logger.error(f"Firestore initialization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Firestore initialization failed: {str(e)}")

def get_firestore_client():
    try:
        return initialize_firestore()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

def get_data(db, collection_name, document_id, expected_type=None):
    """
    Retrieve a document from a Firestore collection based on its document ID. Optionally, 
    verify if the document's type matches an expected type.

    Parameters:
    db (firestore.Client): The Firestore client used to interact with the database.
    collection_name (str): The name of the collection from which to retrieve the document.
    document_id (str): The ID of the document to retrieve.
    expected_type (str, optional): The expected type of the document. This function checks 
        if the 'type' field of the document matches this value. If there is a mismatch, 
        or if the 'type' field is missing, an error message is returned.

    Returns:
    dict or str: If the document exists and, if `expected_type` is provided, matches 
        the expected type, this function returns the document data as a dictionary. 
        If there is a type mismatch or the document does not exist, it returns an 
        error message or `None`, respectively.
    """
    doc_ref = db.collection(collection_name).document(document_id)
    doc = doc_ref.get()
    
    if doc.exists:
        doc_data = doc.to_dict()
    
        # Check if expected_type is provided and matches document type
        if expected_type and ('type' not in doc_data or doc_data['type'] != expected_type):
            return f"Error: Document type does not match expected type '{expected_type}'. Please check the document ID"

        return doc_data
    else:
        raise HTTPException(status_code=404, detail="Requested Challenge Doc is Empty")

def get_subcollection_data(db, main_collection_name, main_document_id, subcollection_name, object_name, expected_type=None):
    """
    Retrieve all documents from a Firestore subcollection and extract a specified object array from each document. Optionally, 
    verify if the document's type matches an expected type.

    Parameters:
    db (firestore.Client): The Firestore client used to interact with the database.
    main_collection_name (str): The name of the main collection.
    main_document_id (str): The ID of the main document.
    subcollection_name (str): The name of the subcollection.
    object_name (str): The name of the object to extract from the documents.
    expected_type (str, optional): The expected type of the subcollection documents. 
        This function checks if the 'type' field of each document matches this value. 
        If there is a mismatch, or if the 'type' field is missing, those documents are ignored.

    Returns:
    list or str: A list containing the specified object arrays from each document in the subcollection 
        that matches the expected type, if provided. Returns an error message if an exception occurs.
    """
    try:
        # Reference to the main collection and document
        main_doc_ref = db.collection(main_collection_name).document(main_document_id)

        # Reference to the subcollection
        subcollection_ref = main_doc_ref.collection(subcollection_name)

        # Fetch all documents in the subcollection
        sub_docs = subcollection_ref.get()

        object_list = []
        for sub_doc in sub_docs:
            if sub_doc.exists:
                sub_doc_data = sub_doc.to_dict()

                # Check if expected_type is provided and matches document type
                if expected_type is None or ('type' in sub_doc_data and sub_doc_data['type'] == expected_type):
                    # Extract the specified object if it exists in the document
                    if object_name in sub_doc_data:
                        object_list.extend(sub_doc_data[object_name])
                        
        if len(object_list) == 0:
            logger.warn("Request yield empty")
            
        return object_list

    except Exception as e:
        logger.error(f"An error occured: {e}")
        raise HTTPException(status_code=404, detail="Requested Subcollection is Empty")
