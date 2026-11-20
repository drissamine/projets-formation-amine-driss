/**
 * Page de réinitialisation de mot de passe - Permet aux utilisateurs de réinitialiser leur mot de passe
 * Interface avec animations et gestion d'erreurs
 */
import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Button, Input, Card, CardBody } from "@heroui/react";
import { FaEnvelope, FaArrowLeft } from "react-icons/fa";
import { motion, AnimatePresence } from "framer-motion";
import ThemeToggle from "../components/ThemeToggle";

const ForgotPassword = () => {
  // État du formulaire
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState(""); // "success" ou "error"

  // Variants d'animation pour les éléments du formulaire
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 15
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage("");
    setMessageType("");

    try {
      // Simulation d'une requête API (fonctionnalité non implémentée)
      await new Promise(resolve => setTimeout(resolve, 1500)); // Délai artificiel

      // Pour l'instant, afficher un message informatif
      setMessage("Cette fonctionnalité n'est pas encore disponible. Veuillez contacter l'administrateur pour réinitialiser votre mot de passe.");
      setMessageType("info");

    } catch (error) {
      console.error("Forgot password error:", error);
      setMessage("Une erreur s'est produite. Veuillez réessayer plus tard.");
      setMessageType("error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen w-full bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 relative">
      {/* Bascule du thème */}
      <div className="absolute top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      {/* Côté gauche - Visuel / Image de marque */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 relative overflow-hidden items-center justify-center p-12 text-white">
        <div className="absolute inset-0 bg-black/10"></div>

        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <motion.div
            animate={{
              y: [0, -20, 0],
              rotate: [0, 5, 0],
            }}
            transition={{
              duration: 6,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="absolute -top-24 -left-24 w-96 h-96 bg-white/10 rounded-full blur-3xl"
          />
          <motion.div
            animate={{
              y: [0, 20, 0],
              rotate: [0, -5, 0],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 2
            }}
            className="absolute top-0 -right-4 w-72 h-72 bg-white/10 rounded-full blur-3xl"
          />
          <motion.div
            animate={{
              y: [0, -15, 0],
              x: [0, 10, 0],
            }}
            transition={{
              duration: 7,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 4
            }}
            className="absolute -bottom-8 left-20 w-80 h-80 bg-white/10 rounded-full blur-3xl"
          />
        </div>

        <div className="z-10 text-center max-w-lg space-y-8">
          <motion.div
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="space-y-4"
          >
            <h1 className="text-6xl font-bold mb-6 tracking-tight bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent">
              Mot de passe oublié ?
            </h1>
            <p className="text-lg text-indigo-100 mb-8 leading-relaxed">
              Pas de souci ! Entrez votre adresse email et nous vous aiderons
              à récupérer l'accès à votre compte.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex gap-6 justify-center"
          >
            <div className="p-6 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 shadow-lg hover:bg-white/15 transition-all duration-300 transform hover:-translate-y-1">
              <div className="text-3xl font-bold">Sécurisé</div>
              <div className="text-sm text-indigo-200 mt-1">Processus sécurisé</div>
            </div>
            <div className="p-6 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 shadow-lg hover:bg-white/15 transition-all duration-300 transform hover:-translate-y-1">
              <div className="text-3xl font-bold">Rapide</div>
              <div className="text-sm text-indigo-200 mt-1">Réinitialisation instantanée</div>
            </div>
          </motion.div>

          {/* Decorative elements */}
          <motion.div
            animate={{
              rotate: 360,
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: "linear"
            }}
            className="absolute -top-10 -right-10 w-20 h-20 border-2 border-white/30 rounded-full"
          />
        </div>
      </div>

      {/* Right Side - Form */}
      <div className="flex w-full lg:w-1/2 items-center justify-center p-8 lg:p-12">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="w-full max-w-md space-y-8"
        >
          {/* Back to Login */}
          <motion.div variants={itemVariants} className="flex items-center">
            <Link
              to="/login"
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            >
              <FaArrowLeft className="text-sm" />
              <span>Retour à la connexion</span>
            </Link>
          </motion.div>

          {/* Header */}
          <motion.div variants={itemVariants} className="text-center">
            <motion.h2
              className="text-4xl font-extrabold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              Réinitialiser le mot de passe
            </motion.h2>
            <motion.p
              className="mt-2 text-sm text-gray-600 dark:text-gray-400"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              Entrez votre adresse email pour recevoir un lien de réinitialisation.
            </motion.p>
          </motion.div>

          <Card className="border-none shadow-xl bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl overflow-hidden">
            <CardBody className="p-8 space-y-6">
              <AnimatePresence>
                {message && (
                  <motion.div
                    initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                    animate={{ opacity: 1, height: 'auto', marginBottom: 24 }}
                    exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`p-4 rounded-lg border-l-4 ${
                      messageType === "success"
                        ? "bg-green-50/50 border-green-500 text-green-700 dark:bg-green-900/20 dark:text-green-300"
                        : messageType === "error"
                        ? "bg-red-50/50 border-red-500 text-red-700 dark:bg-red-900/20 dark:text-red-300"
                        : "bg-blue-50/50 border-blue-500 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className={`text-lg ${messageType === "success" ? "text-green-500" : messageType === "error" ? "text-red-500" : "text-blue-500"}`}>
                        {messageType === "success" ? "✅" : messageType === "error" ? "⚠️" : "ℹ️"}
                      </span>
                      <div>
                        <p className="font-medium">
                          {messageType === "success" ? "Succès" : messageType === "error" ? "Erreur" : "Information"}
                        </p>
                        <p>{message}</p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <motion.form
                onSubmit={handleSubmit}
                className="space-y-6"
                variants={itemVariants}
                initial="hidden"
                animate="visible"
              >
                {/* Email Field */}
                <motion.div variants={itemVariants} className="space-y-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FaEnvelope className="text-gray-400 text-lg dark:text-gray-300" />
                    </div>
                    <Input
                      aria-label="Email"
                      placeholder="votre@email.com"
                      type="email"
                      name="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      variant="bordered"
                      radius="lg"
                      className="pl-10"
                      classNames={{
                        input: "text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400",
                        inputWrapper:
                          "border-gray-300 dark:border-gray-600 hover:border-indigo-500 dark:hover:border-indigo-400 focus-within:!border-indigo-500 dark:focus-within:!border-indigo-400 focus-within:!ring-2 focus-within:!ring-indigo-200 dark:focus-within:!ring-indigo-900/30 transition-all duration-200",
                      }}
                      startContent={<span className="w-6" />}
                    />
                  </div>
                </motion.div>

                {/* Submit Button */}
                <motion.div variants={itemVariants}>
                  <Button
                    type="submit"
                    size="lg"
                    className="w-full bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 text-white font-bold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 hover:scale-105 disabled:scale-100 disabled:opacity-60 disabled:cursor-not-allowed"
                    isLoading={isLoading}
                    disabled={isLoading}
                  >
                    {isLoading ? "Envoi en cours..." : "Envoyer le lien de réinitialisation"}
                  </Button>
                </motion.div>
              </motion.form>

              {/* Demo Account Info */}
              <motion.div variants={itemVariants} className="text-center">
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Pour tester l'application, utilisez le compte démo :
                </p>
                <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mt-1">
                  demo@demo.com / demo123
                </p>
              </motion.div>
            </CardBody>
          </Card>

          {/* Footer */}
          <motion.p
            variants={itemVariants}
            className="text-center text-sm text-gray-600 dark:text-gray-400"
          >
            Pas encore de compte ?{" "}
            <Link
              to="/register"
              className="font-semibold text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300 transition-colors"
            >
              Créer un compte gratuitement
            </Link>
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
};

export default ForgotPassword;
