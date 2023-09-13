function(clone_or_update_git_repository URL REF LOCAL_DIR)
  message("Git repository URL: ${URL}")
  message("Git reference: ${REF}")
  message("Local directory: ${LOCAL_DIR}")

  if(NOT EXISTS ${LOCAL_DIR})
    message("Local directory does not exist. Cloning repository...")
    execute_process(
      COMMAND git clone ${URL} ${LOCAL_DIR}
      RESULT_VARIABLE CLONE_RESULT
    )

    if(NOT CLONE_RESULT EQUAL "0")
      message(FATAL_ERROR "Failed to clone Git repository: ${URL}")
    endif()
  else()
    message("Local directory exists. Checking repository...")

    execute_process(
      COMMAND git -C ${LOCAL_DIR} rev-parse --is-inside-work-tree
      OUTPUT_VARIABLE IS_GIT_REPO
      OUTPUT_STRIP_TRAILING_WHITESPACE
    )

    if(NOT IS_GIT_REPO STREQUAL "true")
      message(FATAL_ERROR "Local directory is not a Git repository")
    endif()

    execute_process(
      COMMAND git -C ${LOCAL_DIR} remote get-url origin
      OUTPUT_VARIABLE ORIGIN_URL
      OUTPUT_STRIP_TRAILING_WHITESPACE
    )

    if(NOT ORIGIN_URL STREQUAL URL)
      message("Updating origin URL...")
      execute_process(
        COMMAND git -C ${LOCAL_DIR} remote set-url origin ${URL}
        RESULT_VARIABLE SET_URL_RESULT
      )

      if(NOT SET_URL_RESULT EQUAL "0")
        message(FATAL_ERROR "Failed to set origin URL: ${URL}")
      endif()
    else()
      message("Origin URL is already set to: ${URL}")
    endif()
  endif()

  execute_process(
    COMMAND git -C ${LOCAL_DIR} symbolic-ref --short HEAD
    OUTPUT_VARIABLE CURRENT_REF
    OUTPUT_STRIP_TRAILING_WHITESPACE
  )

  if(NOT CURRENT_REF STREQUAL REF)
    message("Checking out to reference: ${REF}")
    execute_process(
      COMMAND git -C ${LOCAL_DIR} checkout ${REF}
      RESULT_VARIABLE CHECKOUT_RESULT
    )

    if(NOT CHECKOUT_RESULT EQUAL "0")
      message(FATAL_ERROR "Failed to checkout Git reference: ${REF}")
    endif()
  else()
    message("Current reference is already set to: ${REF}")
  endif()
endfunction()