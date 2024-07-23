import React, { createContext, useRef } from "react";

import useAPI from '../api/apiMain.js'


const GlobalVariables = createContext()

/** 
 * Enables Global Variable sharing across the Site, Also shares the API Calls/Responses needed
*/
export function GlobalVariableProvider({children}) {
    const {sendRequest, returnData, inProgress, requestData} = useAPI()
    
    const Globals = {
        apiSendRequest: sendRequest, apiReturnData: returnData, apiInProgress: inProgress, requestData
    }
    return (
        <GlobalVariables.Provider value={Globals}>
            {children}
        </GlobalVariables.Provider>
    );
}

export default GlobalVariables;
