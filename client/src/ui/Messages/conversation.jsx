import React, {useContext, useState, useEffect} from "react"
import { useLoaderData } from "react-router-dom"
import GlobalVariables from "../../globals/globalVariables"

export default function Conversation() {
    const {chatId} = useLoaderData()
    const Globals = useContext(GlobalVariables)
    const [data, setData] = useState({'Metadata': {'path': ''}, 'Messages': {'inbox': {}}})
    const [inProgress, setInProgress] = useState(true)
    const api = Globals.API
    useEffect(() => {
        api.post('', {'requestType': 'loadConversation', 'chatId': chatId}).then((respo) => {
            setData(respo.data['data'])
        })
        setInProgress(false)
    }, [api, setData])
    return <p>{chatId}</p>
}