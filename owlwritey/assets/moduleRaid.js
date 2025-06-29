/* moduleRaid v5 - Modified for dynamic webpack chunk detection
 * https://github.com/@pedroslopez/moduleRaid
 *
 * Copyright pixeldesu, pedroslopez and other contributors
 * Licensed under the MIT License
 * https://github.com/pedroslopez/moduleRaid/blob/master/LICENSE
 */

const moduleRaid = function () {
  moduleRaid.mID  = Math.random().toString(36).substring(7);
  moduleRaid.mObj = {};

  // Dynamically find webpack chunk array
  function findWebpackChunks() {
    const chunkNames = Object.keys(window).filter(key => 
      key.startsWith('webpackChunk') && Array.isArray(window[key])
    );
    
    if (chunkNames.length === 0) {
      console.error('[moduleRaid] No webpack chunk arrays found. Available window properties:', 
        Object.keys(window).filter(k => k.includes('webpack')));
      return null;
    }
    
    console.log('[moduleRaid] Found webpack chunks:', chunkNames);
    return window[chunkNames[0]]; // Use the first one found
  }

  fillModuleArray = function() {
    const webpackChunks = findWebpackChunks();
    if (!webpackChunks) {
      throw new Error('No webpack chunk array found');
    }
    
    webpackChunks.push([
      [moduleRaid.mID], {}, function(e) {
        Object.keys(e.m).forEach(function(mod) {
          moduleRaid.mObj[mod] = e(mod);
        })
      }
    ]);
  }

  fillModuleArray();

  get = function get (id) {
    return moduleRaid.mObj[id]
  }

  findModule = function findModule (query) {
    results = [];
    modules = Object.keys(moduleRaid.mObj);

    modules.forEach(function(mKey) {
      mod = moduleRaid.mObj[mKey];

      if (typeof mod !== 'undefined') {
        if (typeof query === 'string') {
          if (typeof mod.default === 'object') {
            for (key in mod.default) {
              if (key == query) results.push(mod);
            }
          }

          for (key in mod) {
            if (key == query) results.push(mod);
          }
        } else if (typeof query === 'function') { 
          if (query(mod)) {
            results.push(mod);
          }
        } else {
          throw new TypeError('findModule can only find via string and function, ' + (typeof query) + ' was passed');
        }
        
      }
    })

    return results;
  }

  return {
    modules: moduleRaid.mObj,
    constructors: moduleRaid.cArr,
    findModule: findModule,
    get: get
  }
}

if (typeof module === 'object' && module.exports) {
  module.exports = moduleRaid;
} else {
  window.mR = moduleRaid();
}
