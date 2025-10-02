import { createContext, useReducer } from "react";

export const PostList = createContext({
  postlist: [],
  addPost: () => {},
  deletePost: () => {},
  addIntialPosts: () => {},
});

const PostListReducer = (currentPostList, action) => {
  let newPostList = currentPostList;
  if (action.type === "DELETE_POST") {
    newPostList = currentPostList.filter(
      (post) => post.id !== action.payload.id
    );
  } else if (action.type === "ADD_POST") {
    newPostList = [action.payload, ...currentPostList];
  } else if (action.type === "ADD_INITIAL_POSTS") {
    newPostList = action.payload.posts;
  }
  return newPostList;
};

const PostListProvider = ({ children }) => {
  const addPost = (userid, title, body, reaction, tags) => {
    dispatchPostList({
      type: "ADD_POST",
      payload: {
        id: Date.now(),
        title: title,
        body: body,
        reactions: reaction,
        userId: userid,
        tags: tags,
      },
    });
  };

  const addIntialPosts = (posts) => {
    dispatchPostList({
      type: "ADD_INITIAL_POSTS",
      payload: {
        posts,
      },
    });
  };

  const deletePost = (id) => {
    console.log(`delete ${id}`);
    dispatchPostList({
      type: "DELETE_POST",
      payload: {
        id: id,
      },
    });
  };
  const [postList, dispatchPostList] = useReducer(PostListReducer, []);

  return (
    <PostList.Provider
      value={{ postList, addPost, deletePost, addIntialPosts }}
    >
      {children}
    </PostList.Provider>
  );
};

export default PostListProvider;
