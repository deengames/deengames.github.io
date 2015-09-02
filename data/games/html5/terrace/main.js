/* Generated by Opal 0.8.0 */
(function(Opal) {
  Opal.dynamic_require_severity = "error";
  function $rb_plus(lhs, rhs) {
    return (typeof(lhs) === 'number' && typeof(rhs) === 'number') ? lhs + rhs : lhs['$+'](rhs);
  }
  var self = Opal.top, $scope = Opal, nil = Opal.nil, $breaker = Opal.breaker, $slice = Opal.slice, $klass = Opal.klass, $hash2 = Opal.hash2;

  Opal.add_stubs(['$each', '$entity=', '$respond_to?', '$send', '$to_proc', '$raise', '$collect', '$to_s', '$class', '$attr_accessor', '$private', '$require', '$to_n', '$Native', '$crafty_name', '$include?', '$sub', '$e', '$init', '$background', '$load', '$create', '$new', '$image', '$w', '$h', '$fourway', '$attr', '$color', '$x', '$bind', '$add', '$audio', '$[]', '$==', '$play', '$textFont', '$textColor', '$text', '$load_content', '$lambda', '$move_with_keyboard', '$move', '$touch', '$launch']);
  (function($base, $super) {
    function $Entity(){};
    var self = $Entity = $klass($base, $super, 'Entity', $Entity);

    var def = self.$$proto, $scope = self.$$scope, TMP_2;

    def.components = nil;
    def.$initialize = function(components) {
      var $a, $b, TMP_1, self = this;

      components = $slice.call(arguments, 0);
      self.components = components;
      return ($a = ($b = self.components).$each, $a.$$p = (TMP_1 = function(c){var self = TMP_1.$$s || this, $a, $b;
if (c == null) c = nil;
      return (($a = [self]), $b = c, $b['$entity='].apply($b, $a), $a[$a.length-1])}, TMP_1.$$s = self, TMP_1), $a).call($b);
    };

    return (def.$method_missing = TMP_2 = function(m, args) {try {

      var $a, $b, TMP_3, $c, TMP_4, self = this, $iter = TMP_2.$$p, block = $iter || nil;

      args = $slice.call(arguments, 1);
      TMP_2.$$p = null;
      ($a = ($b = self.components).$each, $a.$$p = (TMP_3 = function(c){var self = TMP_3.$$s || this, $a, $b, to_return = nil;
if (c == null) c = nil;
      if ((($a = c['$respond_to?'](m)) !== nil && (!$a.$$is_boolean || $a == true))) {
          to_return = ($a = ($b = c).$send, $a.$$p = block.$to_proc(), $a).apply($b, [m].concat(args));
          Opal.ret(to_return);
          } else {
          return nil
        }}, TMP_3.$$s = self, TMP_3), $a).call($b);
      return self.$raise("No method named '" + (m) + "' was found on this entity or any of its components: " + (($a = ($c = self.components).$collect, $a.$$p = (TMP_4 = function(o){var self = TMP_4.$$s || this;
if (o == null) o = nil;
      return o.$class().$to_s()}, TMP_4.$$s = self, TMP_4), $a).call($c)));
      } catch ($returner) { if ($returner === Opal.returner) { return $returner.$v } throw $returner; }
    }, nil) && 'method_missing';
  })(self, null);
  (function($base, $super) {
    function $BaseComponent(){};
    var self = $BaseComponent = $klass($base, $super, 'BaseComponent', $BaseComponent);

    var def = self.$$proto, $scope = self.$$scope;

    self.$attr_accessor("entity");

    self.$private();

    return (def.$initialize = function() {
      var self = this;

      return nil;
    }, nil) && 'initialize';
  })(self, null);
  self.$require("native");
  (function($base, $super) {
    function $Crafty(){};
    var self = $Crafty = $klass($base, $super, 'Crafty', $Crafty);

    var def = self.$$proto, $scope = self.$$scope;

    Opal.defs(self, '$init', function(width, height) {
      var self = this;

      return Crafty.init(width, height);
    });

    Opal.defs(self, '$load', function(files, onComplete) {
      var self = this;

      files = files.$to_n();
      return Crafty.load(files, onComplete);
    });

    Opal.defs(self, '$background', function(color) {
      var self = this;

      return Crafty.background(color);
    });

    Opal.defs(self, '$e', function(components) {
      var self = this;

      return self.$Native(Crafty.e(components));
    });

    return (Opal.defs(self, '$audio', function() {
      var self = this;

      return self.$Native(Crafty.audio);
    }), nil) && 'audio';
  })(self, null);
  (function($base, $super) {
    function $Entity(){};
    var self = $Entity = $klass($base, $super, 'Entity', $Entity);

    var def = self.$$proto, $scope = self.$$scope;

    def.components = nil;
    return (def.$initialize = function(components) {
      var $a, $b, TMP_5, $c, TMP_6, self = this, component_names = nil;

      components = $slice.call(arguments, 0);
      self.components = components;
      component_names = "2D, Canvas,";
      ($a = ($b = self.components).$each, $a.$$p = (TMP_5 = function(c){var self = TMP_5.$$s || this;
if (c == null) c = nil;
      return component_names = "" + (component_names) + " " + (c.$crafty_name()) + ", "}, TMP_5.$$s = self, TMP_5), $a).call($b);
      if ((($a = ($c = component_names['$include?']("Text"), $c !== false && $c !== nil ?component_names['$include?']("Color") : $c)) !== nil && (!$a.$$is_boolean || $a == true))) {
        component_names = component_names.$sub("Color,", "")};
      self.me = $scope.get('Crafty').$e(component_names);
      return ($a = ($c = self.components).$each, $a.$$p = (TMP_6 = function(c){var self = TMP_6.$$s || this, $a, $b;
        if (self.me == null) self.me = nil;
if (c == null) c = nil;
      return (($a = [self.me]), $b = c, $b['$entity='].apply($b, $a), $a[$a.length-1])}, TMP_6.$$s = self, TMP_6), $a).call($c);
    }, nil) && 'initialize'
  })(self, null);
  (function($base, $super) {
    function $Game(){};
    var self = $Game = $klass($base, $super, 'Game', $Game);

    var def = self.$$proto, $scope = self.$$scope;

    def.$initialize = function(width, height) {
      var self = this;

      $scope.get('Crafty').$init(width, height);
      return $scope.get('Crafty').$background("black");
    };

    def.$load_content = function(files, callback) {
      var self = this;

      return $scope.get('Crafty').$load(files, callback);
    };

    def.$create = function() {
      var self = this;

      return nil;
    };

    return (Opal.defs(self, '$launch', function(game_class) {
      var self = this;

      return game_class.$new().$create();
    }), nil) && 'launch';
  })(self, null);
  (function($base, $super) {
    function $ImageComponent(){};
    var self = $ImageComponent = $klass($base, $super, 'ImageComponent', $ImageComponent);

    var def = self.$$proto, $scope = self.$$scope;

    def.entity = nil;
    def.$image = function(string) {
      var self = this;

      return self.entity.$image(string);
    };

    def.$width = function() {
      var self = this;

      return self.entity.$w();
    };

    def.$height = function() {
      var self = this;

      return self.entity.$h();
    };

    return (def.$crafty_name = function() {
      var self = this;

      return "Image, Alpha";
    }, nil) && 'crafty_name';
  })(self, $scope.get('BaseComponent'));
  (function($base, $super) {
    function $KeyboardComponent(){};
    var self = $KeyboardComponent = $klass($base, $super, 'KeyboardComponent', $KeyboardComponent);

    var def = self.$$proto, $scope = self.$$scope;

    def.entity = nil;
    def.$move_with_keyboard = function() {
      var self = this;

      return self.entity.$fourway(128);
    };

    return (def.$crafty_name = function() {
      var self = this;

      return "Fourway";
    }, nil) && 'crafty_name';
  })(self, $scope.get('BaseComponent'));
  (function($base, $super) {
    function $TwoDComponent(){};
    var self = $TwoDComponent = $klass($base, $super, 'TwoDComponent', $TwoDComponent);

    var def = self.$$proto, $scope = self.$$scope;

    def.entity = nil;
    def.$size = function(width, height) {
      var self = this;

      return self.entity.$attr($hash2(["w", "h"], {"w": width, "h": height}));
    };

    def.$move = function(x, y) {
      var self = this;

      return self.entity.$attr($hash2(["x", "y"], {"x": x, "y": y}));
    };

    def.$color = function(color) {
      var self = this;

      return self.entity.$color(color);
    };

    def.$x = function() {
      var self = this;

      return self.entity.$x();
    };

    def.$y = function() {
      var self = this;

      return self.entity.$x();
    };

    return (def.$crafty_name = function() {
      var self = this;

      return "Color";
    }, nil) && 'crafty_name';
  })(self, $scope.get('BaseComponent'));
  (function($base, $super) {
    function $TouchComponent(){};
    var self = $TouchComponent = $klass($base, $super, 'TouchComponent', $TouchComponent);

    var def = self.$$proto, $scope = self.$$scope;

    def.entity = nil;
    def.$touch = function(callback) {
      var self = this;

      return self.entity.$bind("Click", callback);
    };

    return (def.$crafty_name = function() {
      var self = this;

      return "Mouse";
    }, nil) && 'crafty_name';
  })(self, $scope.get('BaseComponent'));
  (function($base, $super) {
    function $AudioComponent(){};
    var self = $AudioComponent = $klass($base, $super, 'AudioComponent', $AudioComponent);

    var def = self.$$proto, $scope = self.$$scope;

    def.$play = function(filename, options) {
      var $a, self = this, key = nil, loop = nil;

      if (options == null) {
        options = $hash2([], {})
      }
      key = filename;
      $scope.get('Crafty').$audio().$add(key, filename);
      loop = ((($a = options['$[]']("loop")) !== false && $a !== nil) ? $a : false);
      loop = (function() {if ((($a = (loop['$=='](true))) !== nil && (!$a.$$is_boolean || $a == true))) {
        return -1
        } else {
        return 1
      }; return nil; })();
      return $scope.get('Crafty').$audio().$play(key, loop);
    };

    return (def.$crafty_name = function() {
      var self = this;

      return "";
    }, nil) && 'crafty_name';
  })(self, $scope.get('BaseComponent'));
  (function($base, $super) {
    function $TextComponent(){};
    var self = $TextComponent = $klass($base, $super, 'TextComponent', $TextComponent);

    var def = self.$$proto, $scope = self.$$scope;

    def.entity = nil;
    def.$text = function(text) {
      var self = this;

      self.entity.$textFont($hash2(["size"], {"size": "15px"}));
      self.entity.$textColor("FFFFFF");
      return self.entity.$text(text);
    };

    def.$move = function(x, y) {
      var self = this;

      return self.entity.$attr($hash2(["x", "y"], {"x": x, "y": y}));
    };

    return (def.$crafty_name = function() {
      var self = this;

      return "Text";
    }, nil) && 'crafty_name';
  })(self, $scope.get('BaseComponent'));
  (function($base, $super) {
    function $MainGame(){};
    var self = $MainGame = $klass($base, $super, 'MainGame', $MainGame);

    var def = self.$$proto, $scope = self.$$scope, TMP_7, TMP_8;

    def.$initialize = TMP_7 = function() {
      var self = this, $iter = TMP_7.$$p, $yield = $iter || nil;

      TMP_7.$$p = null;
      return Opal.find_super_dispatcher(self, 'initialize', TMP_7, null).apply(self, [800, 600]);
    };

    return (def.$create = TMP_8 = function() {var $zuper = $slice.call(arguments, 0);
      var $a, $b, TMP_9, self = this, $iter = TMP_8.$$p, $yield = $iter || nil;

      TMP_8.$$p = null;
      Opal.find_super_dispatcher(self, 'create', TMP_8, $iter).apply(self, $zuper);
      return self.$load_content($hash2(["images", "audio"], {"images": ["content/images/fox.png", "content/images/background.jpg"], "audio": ["content/audio/noise.ogg"]}), ($a = ($b = self).$lambda, $a.$$p = (TMP_9 = function(){var self = TMP_9.$$s || this, $a, $b, TMP_10, e = nil, touches = nil, t = nil;

      $scope.get('Entity').$new($scope.get('TwoDComponent').$new(), $scope.get('ImageComponent').$new()).$image("content/images/background.jpg");
        e = $scope.get('Entity').$new($scope.get('ImageComponent').$new(), $scope.get('KeyboardComponent').$new(), $scope.get('TwoDComponent').$new(), $scope.get('TouchComponent').$new(), $scope.get('AudioComponent').$new());
        e.$image("content/images/fox.png");
        e.$move_with_keyboard();
        touches = 0;
        t = $scope.get('Entity').$new($scope.get('TextComponent').$new(), $scope.get('TwoDComponent').$new());
        t.$text("Touches: 0");
        t.$move(8, 8);
        return e.$touch(($a = ($b = self).$lambda, $a.$$p = (TMP_10 = function(){var self = TMP_10.$$s || this;

        e.$play("content/audio/noise.ogg");
          touches = $rb_plus(touches, 1);
          return t.$text("Touches: " + (touches));}, TMP_10.$$s = self, TMP_10), $a).call($b));}, TMP_9.$$s = self, TMP_9), $a).call($b));
    }, nil) && 'create';
  })(self, $scope.get('Game'));
  return $scope.get('Game').$launch($scope.get('MainGame'));
})(Opal);
