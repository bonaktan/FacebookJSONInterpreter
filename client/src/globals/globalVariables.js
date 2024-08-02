import React, { createContext} from "react";
import axios from "axios";


const GlobalVariables = createContext()

/** 
 * Enables Global Variable sharing across the Site, Also shares the API Calls/Responses needed
*/
export function GlobalVariableProvider({children}) {
    const API = axios.create({
        baseURL: "http://127.0.0.1:42069/api" 
    });
    const Globals = {
        API
    }
    return (
        <GlobalVariables.Provider value={Globals}>
            {children}
        </GlobalVariables.Provider>
    );
}

export default GlobalVariables;
