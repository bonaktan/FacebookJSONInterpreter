import React from "react";
import { createBrowserRouter, createRoutesFromElements, BrowserRouter, RouterProvider, Routes, Route, Outlet, Link } from "react-router-dom";

import FolderFetch from './Home/FolderFetch'
import Messages from "./Messages/main";
import Conversation from "./Messages/conversation";

export default function FacebookJSONInterpreter() {
    const router = createBrowserRouter(createRoutesFromElements(
        <Route path='/' element={<Header />}>
            <Route index element={<FolderFetch />} />
            <Route path='messages' element={<Messages />} />
            <Route
                path="messages/:chatId"
                loader={({params}) => {return {chatId: params.chatId}}}
                element={<Conversation/>}
            />
        </Route>
    ))
    return (
        <RouterProvider router={router} />
    );
}

const Header = () => { return (
    <>
        <div>
            <div><p>Facebook JSON Interpreter</p></div>
            <div><p>Made By: bonnybonnybonaktan</p></div>
        </div>
        <br />
        <Outlet />
    </>
)}