import Post from "./Post";
import { PostList as PostListData } from "../store/post-list-store";
import { useContext, useEffect, useState } from "react";
import WelcomeMessage from "./WelcomeMessage";
import LoadingSpinner from "./LoadingSpinner";
function PostList() {
  const { postList, addIntialPosts } = useContext(PostListData);
  const [fetching, setfetching] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;
    setfetching(true);
    fetch("https://dummyjson.com/posts", { signal })
      .then((res) => res.json())
      .then((data) => {
        addIntialPosts(data.posts);
        setfetching(false);
      });
    return () => {
      console.log("Cleaning up");
      controller.abort();
    };
  }, []);

  return (
    <>
      {fetching && <LoadingSpinner></LoadingSpinner>}
      {!fetching && postList.length === 0 && <WelcomeMessage></WelcomeMessage>}
      {!fetching &&
        postList.map((post) => <Post key={post.id} post={post}></Post>)}
    </>
  );
}

export default PostList;
