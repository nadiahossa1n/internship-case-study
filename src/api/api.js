export const getAIMessage = async (userQuery) => {
  try {
    const response = await fetch("http://127.0.0.1:5000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: userQuery }),
    });

    // Check if the response is OK (status code 200)
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const data = await response.json();

    // Ensure that response is a string
    if (typeof data.response === "string") {
      return {
        role: "assistant",
        content: data.response,
      };
    } else {
      // If the response is an object, convert it to a string
      return {
        role: "assistant",
        content: JSON.stringify(data.response),
      };
    }
  } catch (error) {
    console.error("Error fetching AI message:", error);
    return {
      role: "assistant",
      content: "Sorry, I couldn't get a response from the AI.",
    };
  }
};
