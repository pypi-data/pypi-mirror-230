import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"

import React, { ReactNode } from "react"

/**
 * This type defines the shape of the `.data` property of the `MessageEvent`
 * received in the `listener()` function of the `NotificationCenter` component.
 * 
 * Type must be "nc" or it will be ignored and it must be present. The target
 * will be come the key of the NotificationCenter data in the streamlit 
 * state object. Payload can be anything and they will be appended to an array
 * value keyed by the target string.
 * 
 * So as an example, if the following code is executed:
 * 
 * ```
 * let target = 'foo'
 * let body = { name: 'Brielle', gender: 'Female' }
 * 
 * Array.from(window.parent.frames).forEach((frame) => {
 *   frame.postMessage({target: target, type: "nc", payload: body}, "*")
 * })
 * ```
 * 
 * Then in streamlit, the `st.session_state._nc_data` value will be a dict
 * with a key 'foo' which maps to an array and, the first time this is executed,
 * the array will have the value [{ 'name': 'Brielle', 'gender': 'Female' }]
 */
export type NotificationMessage = {
  type: 'nc';
  target?: string;
  payload?: any;
  from?: string;
  command?: null | 'clear' | 'clear-all';
}

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */
class NotificationCenter extends StreamlitComponentBase<{}> {
  /**
   * Add an event listener for postMessages by attaching a 'message' listener
   */  
  public componentDidMount(): void {
    window.addEventListener('message', this.listener)  
  }

  /**
   * Remove the event listener for 'message' when the component is unmounted
   */
  public componentWillUnmount(): void {
    window.removeEventListener('message', this.listener)
  }

  /**
   * Validates a message received as Event.data in the window's 'message' event listener
   * 
   * @param message the .data portion of a browser event. If the contents of the supplied
   * object match the type definition of NotificationMessage, true is returned.
   * @returns true if the format matches; false otherwise
   */
  public static isValidMessage(message: any): message is NotificationMessage {
    if (!message || message.type !== "nc") { return false }
    if (message.command && message.command === "clear-all") { return true }
    if (!message.target) { return false }
    if (message.command && message.command === "clear") { return true }
    if (!message.payload) { return false }
    return true
  }

  /**
   * The listener is used to listen for `postMessage` events being fired in the browser
   * window. The `NotificationCenter` type only acknowledges event messages that meet the
   * `NotificationMessage` type. All other types are ignored and dropped. On a successful
   * message, Streamlit will rerender the UI after the data is sent back to it.
   * 
   * @param event a browser 'messages' event type
   */
  public listener(event: MessageEvent) {
    const message = event?.data
    
    if (NotificationCenter.isValidMessage(message)) {      
      Streamlit.setComponentValue(message)
    }
  }

  /**
   * Renders a zero space invisible component that simply listens on the page for any
   * postMessage events to propagate. All messages are listened for. Any matching
   * messages are processed by the listener() method and successful ones are passed 
   * up to Streamlit.
   * 
   * @returns an invisible component to place on the page.
   */
  public render = (): ReactNode => {
    // Supplied key
    const key = this.props.args["key"] ?? "unkeyed"

    // Create an invisible, non-layout component that when mounted will setup a
    // listener 
    return (
      <><span 
        className={`notification-center ${key}`} 
        style={{display: "none"}}
      ></span></>
    )
  }
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(NotificationCenter)
