import React from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import { motion, AnimatePresence } from "framer-motion";

import Search from './pages/Search';
import Recommend from './pages/Recommend';
import Landing from './pages/Landing';


const App = () => {
  return (
    <Router>
      <AnimatePresence>
        <Switch>
		<Route exact path="/">
            <motion.div
              key="landing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Landing />
            </motion.div>
          </Route>
          <Route exact path="/search">
            <motion.div
              key="search"
              initial={{ x: window.innerWidth, opacity: 1 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -window.innerWidth, opacity: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Search />
            </motion.div>
          </Route>
          <Route exact path="/recommend">
            <motion.div
              key="recommend"
              initial={{ x: window.innerWidth, opacity: 1 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -window.innerWidth, opacity: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Recommend />
            </motion.div>
          </Route>
        </Switch>
      </AnimatePresence>
    </Router>
  );
};

export default App;