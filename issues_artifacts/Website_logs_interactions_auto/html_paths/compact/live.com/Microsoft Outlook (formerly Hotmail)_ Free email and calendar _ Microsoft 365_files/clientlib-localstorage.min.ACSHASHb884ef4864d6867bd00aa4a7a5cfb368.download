/*
*Utility class for handling data storage in the browser's local storage with encoding/decoding support.
*Note: This class is designed for storing and retrieving objects in local storage. 
*/ 

class LocalStorageUtil {
    constructor(opts) {
      // Set the storage key from options, defaulting to an empty object
      this.storageKey = opts.storageKey || {}; 
    }
  
    /**
     * Encode the value before storing in local storage
     */
    encodeValue = (value) => {
      if(!value) {
        return {};
      }
  
      let encodedValue;
      try {
        encodedValue =  window.btoa(JSON.stringify(value));
      } catch(error) {
        encodedValue = value
      }
      return encodedValue;
    };
  
    /**
     * Decode the value retrieved from local storage
     */
    decodeValue = (encodedValue) => {
      if(!encodedValue) {
        return {};
      }
      let decodedValue;
      try {
        decodedValue = window.atob(encodedValue); // Decode the encoded value
      } catch (error) {
        decodedValue = encodedValue; // If decoding fails, return the original value
      }
      return decodedValue;
    };
  
    /**
     * Check if an object is empty
     */
    isEmptyObject = (obj) => {
      return Object.keys(obj).length === 0;
    };
  
    /**
     * Set an item in local storage
     */
    setItem = (key, value) => {
      // Retrieve existing data from local storage
      let storedData = localStorage.getItem(this.storageKey) || {}; 
      // Decode the existing data
      if (!this.isEmptyObject(storedData)) {
        storedData = JSON.parse(this.decodeValue(storedData));
      }
      // Update the value for the given key
      storedData[key] = value; 
      // Encode the updated data
      storedData = this.encodeValue(storedData); 
      // Save the updated data to local storage
      localStorage.setItem(this.storageKey, storedData); 
    };
  
    /**
     * Get the value for a given key from local storage
     */
    getItem = (key) => {
      // Retrieve data from local storage
      let storedData = localStorage.getItem(this.storageKey) || {}; 
      // Decode the retrieved data
      if(this.isEmptyObject(storedData)) {
        return null
      }
  
      storedData = JSON.parse(this.decodeValue(storedData)); 
      if (!this.isEmptyObject(storedData)) {
        // Return the value for the given key, or null if it doesn't exist
        return storedData[key] || null; 
      }
    };
  
    /**
     * Remove an item from local storage for the given key
     */
    removeItem = (key) => {
      // Retrieve existing data from local storage
      const storedData = JSON.parse(this.decodeValue(localStorage.getItem(this.storageKey))) || {}; 
      // Remove the value for the given key 
      delete storedData[key]; 
      storedData = this.encodeValue(storedData); 
      // Save the updated data to local storage
      localStorage.setItem(this.storageKey, JSON.stringify(storedData)); 
    };
  
    /**
     * Clear the entire local storage
     */
    clear = () => {
      localStorage.removeItem(this.storageKey);
    };
  }