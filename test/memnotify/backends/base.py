"""Base memnotify backend class."""


class BaseMemnotifyBackend(object):
    """
    Base class for memnotify backend implementations.

	Subclasses must overwrite these methods. Open and close methods are optionals.

	open() and close() can be called indirectly by using a backend object as a
	context manager:

       with backend as connection:
           # do something with connection
           pass
    """
    def open(self):
        """Open a new network connection with the backend server.

        This method can be overwritten by backend implementations to
        open a network connection.

        The default implementation does nothing.
        """
        pass

    def close(self):
        """Close a network connection."""
        pass

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def send(self, user, content, level, sender=None, expired_at=None, one_time=False):
    	"""
    	Sends a message to a user using the memory storage backend.
    	"""
    	raise NotImplementedError('subclasses of BaseMemNotifyBackend must override send() method')

    def num_unread(self, user):
    	"""
    	Gets the number of unread messages for an user.
    	"""
    	raise NotImplementedError('subclasses of BaseMemNotifyBackend must override num_unread() method')

    def get_messages(self, user):
    	"""
    	Gets all messages to an user.
    	"""
    	raise NotImplementedError('subclasses of BaseMemNotifyBackend must override get_messages() method')

    def get_last_and_read(self, user):
    	"""
    	Gets the last message to an user an mark it as read.
    	"""
    	raise NotImplementedError('subclasses of BaseMemNotifyBackend must override get_last_and_read() method')

    def mark_all_as_read(self, user):
    	"""
    	Marks all messages to an user as read.
    	"""
    	raise NotImplementedError('subclasses of BaseMemNotifyBackend must override mark_all_as_read() method')

    def global_send(self, content, level, sender=None, expired_at=None):
    	"""
    	Sends a global message using the memory storage backend.
    	"""
    	raise NotImplementedError('subclasses of BaseMemNotifyBackend must override global_send() method')

    def global_num_unread(self):
    	"""
    	Gets the number of global messages.
    	"""
    	raise NotImplementedError('subclasses of BaseMemNotifyBackend must override global_num_unread() method')

    def global_get_messages(self):
    	"""
    	Gets all global messages.
    	"""
    	raise NotImplementedError('subclasses of BaseMemNotifyBackend must override global_get_messages() method')